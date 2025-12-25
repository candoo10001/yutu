"""
Video generation module using Kling O1 API.
"""
import time
from pathlib import Path
from typing import Optional

import jwt
import requests
import structlog

from .config import Config
from .utils.error_handler import KlingAPIError
from .utils.logger import log_api_call, log_api_response, log_error


class VideoGenerator:
    """Generates videos using Kling O1 API."""

    def __init__(self, config: Config, logger: Optional[structlog.BoundLogger] = None):
        """
        Initialize the Video Generator.

        Args:
            config: Configuration instance
            logger: Logger instance
        """
        self.config = config
        self.logger = logger or structlog.get_logger()
        self.access_key = config.kling_access_key
        self.secret_key = config.kling_secret_key
        self.base_url = "https://api.klingai.com"  # Placeholder - adjust based on actual API

    def _generate_jwt_token(self) -> str:
        """
        Generate a JWT token for Kling API authentication.

        Returns:
            JWT token string

        Raises:
            KlingAPIError: If token generation fails
        """
        try:
            headers = {
                "alg": "HS256",
                "typ": "JWT"
            }
            payload = {
                "iss": self.access_key,  # Access Key as issuer
                "exp": int(time.time()) + 1800,  # Token expires in 30 minutes
                "nbf": int(time.time()) - 5  # Token is valid from 5 seconds ago
            }
            token = jwt.encode(payload, self.secret_key, algorithm="HS256", headers=headers)
            return token
        except Exception as e:
            log_error(self.logger, e, "video_generator._generate_jwt_token")
            raise KlingAPIError(f"Failed to generate JWT token: {str(e)}")

    def generate_video_from_image(self, image_path: str, prompt: str, output_dir: str = "output") -> str:
        """
        Generate a video from an image using Kling Omni Video API.

        Args:
            image_path: Path to the input image
            prompt: Video generation prompt (optional, for guidance)
            output_dir: Directory to save the generated video

        Returns:
            Path to the generated video file

        Raises:
            KlingAPIError: If video generation fails
        """
        start_time = time.time()

        log_api_call(
            self.logger,
            "Kling API",
            "generate_video_from_image",
            image_path=image_path,
            prompt_length=len(prompt) if prompt else 0,
            duration=self.config.kling_video_duration
        )

        try:
            # Step 1: Submit generation request with image
            task_id = self._submit_image_to_video_request(image_path, prompt)

            # Step 2: Poll for completion
            video_url = self._poll_generation_status(task_id)

            # Step 3: Download video
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            video_file = output_path / f"video_{int(time.time())}.mp4"

            self._download_video(video_url, str(video_file))

            duration_ms = (time.time() - start_time) * 1000

            log_api_response(
                self.logger,
                "Kling API",
                "generate_video_from_image",
                success=True,
                duration_ms=duration_ms,
                task_id=task_id,
                video_path=str(video_file)
            )

            self.logger.info(
                "video_generated_from_image",
                video_path=str(video_file),
                generation_time_seconds=int(duration_ms / 1000)
            )

            return str(video_file)

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_api_response(
                self.logger,
                "Kling API",
                "generate_video_from_image",
                success=False,
                duration_ms=duration_ms,
                error=str(e)
            )
            raise

    def generate_video(self, prompt: str, output_dir: str = "output") -> str:
        """
        Generate a video from a text prompt.

        Args:
            prompt: Video generation prompt
            output_dir: Directory to save the generated video

        Returns:
            Path to the generated video file

        Raises:
            KlingAPIError: If video generation fails
        """
        start_time = time.time()

        log_api_call(
            self.logger,
            "Kling API",
            "generate_video",
            prompt_length=len(prompt),
            duration=self.config.kling_video_duration
        )

        try:
            # Step 1: Submit generation request
            task_id = self._submit_generation_request(prompt)

            # Step 2: Poll for completion
            video_url = self._poll_generation_status(task_id)

            # Step 3: Download video
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            video_file = output_path / f"video_{int(time.time())}.mp4"

            self._download_video(video_url, str(video_file))

            duration_ms = (time.time() - start_time) * 1000

            log_api_response(
                self.logger,
                "Kling API",
                "generate_video",
                success=True,
                duration_ms=duration_ms,
                task_id=task_id,
                video_path=str(video_file)
            )

            self.logger.info(
                "video_generated",
                video_path=str(video_file),
                generation_time_seconds=int(duration_ms / 1000)
            )

            return str(video_file)

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_api_response(
                self.logger,
                "Kling API",
                "generate_video",
                success=False,
                duration_ms=duration_ms,
                error=str(e)
            )
            raise

    def _submit_image_to_video_request(self, image_path: str, prompt: str) -> str:
        """
        Submit an image-to-video generation request to Kling API.

        Args:
            image_path: Path to the input image
            prompt: Video generation prompt

        Returns:
            Task ID for tracking generation progress

        Raises:
            KlingAPIError: If request submission fails
        """
        url = f"{self.base_url}/v1/videos/omni-video"

        # Generate JWT token for authentication
        jwt_token = self._generate_jwt_token()

        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        }

        # Read and encode image as base64
        import base64
        try:
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            raise KlingAPIError(f"Failed to read image file: {str(e)}")

        payload = {
            "image_list": [
                {
                    "image_url": image_data,
                    "type": "first_frame"
                }
            ],
            "prompt": prompt,
            "duration": self.config.kling_video_duration,
            "mode": "pro",
            "aspect_ratio": "16:9"
        }

        try:
            self.logger.info("submitting_image_to_video_request", image_path=image_path)

            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=30
            )

            # Debug: Log the actual response
            self.logger.info("kling_api_response",
                           status_code=response.status_code,
                           response_text=response.text[:500])

            if response.status_code == 401:
                raise KlingAPIError("Invalid Kling API key", status_code=401)
            elif response.status_code == 429:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("message", "Rate limit exceeded")
                except:
                    error_msg = "Rate limit exceeded"
                raise KlingAPIError(f"Kling API Error: {error_msg}", status_code=429)
            elif response.status_code != 200:
                raise KlingAPIError(
                    f"Failed to submit generation request: {response.text}",
                    status_code=response.status_code
                )

            data = response.json()
            task_id = data.get("data", {}).get("task_id")

            if not task_id:
                raise KlingAPIError("No task ID in response")

            self.logger.info("generation_request_submitted", task_id=task_id)

            return task_id

        except requests.RequestException as e:
            log_error(self.logger, e, "video_generator._submit_image_to_video_request")
            raise KlingAPIError(f"Network error submitting request: {str(e)}")

    def _submit_generation_request(self, prompt: str) -> str:
        """
        Submit a video generation request to Kling API.

        Args:
            prompt: Video generation prompt

        Returns:
            Task ID for tracking generation progress

        Raises:
            KlingAPIError: If request submission fails
        """
        url = f"{self.base_url}/v1/videos/omni-video"

        # Generate JWT token for authentication
        jwt_token = self._generate_jwt_token()

        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "prompt": prompt,
            "duration": self.config.kling_video_duration,
            "aspect_ratio": "16:9",
            "mode": "pro"  # Standard mode
        }

        try:
            self.logger.info("submitting_video_generation_request")

            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=30
            )

            # Debug: Log the actual response
            self.logger.info("kling_api_response",
                           status_code=response.status_code,
                           response_text=response.text[:500])

            if response.status_code == 401:
                raise KlingAPIError("Invalid Kling API key", status_code=401)
            elif response.status_code == 429:
                # Parse the actual error message from Kling
                try:
                    error_data = response.json()
                    error_msg = error_data.get("message", "Rate limit exceeded")
                except:
                    error_msg = "Rate limit exceeded"
                raise KlingAPIError(f"Kling API Error: {error_msg}", status_code=429)
            elif response.status_code != 200:
                raise KlingAPIError(
                    f"Failed to submit generation request: {response.text}",
                    status_code=response.status_code
                )

            data = response.json()
            task_id = data.get("data", {}).get("task_id")

            if not task_id:
                raise KlingAPIError("No task ID in response")

            self.logger.info("generation_request_submitted", task_id=task_id)

            return task_id

        except requests.RequestException as e:
            log_error(self.logger, e, "video_generator._submit_generation_request")
            raise KlingAPIError(f"Network error submitting request: {str(e)}")

    def _poll_generation_status(
        self,
        task_id: str,
        max_wait_seconds: int = 600,
        poll_interval: int = 15
    ) -> str:
        """
        Poll Kling API for video generation completion.

        Args:
            task_id: Task ID from generation request
            max_wait_seconds: Maximum time to wait (default: 10 minutes)
            poll_interval: Seconds between polls (default: 15 seconds)

        Returns:
            URL of the generated video

        Raises:
            KlingAPIError: If polling fails or times out
        """
        url = f"{self.base_url}/v1/videos/text2video/{task_id}"

        # Generate JWT token for authentication
        jwt_token = self._generate_jwt_token()

        headers = {
            "Authorization": f"Bearer {jwt_token}"
        }

        start_time = time.time()
        attempt = 0

        self.logger.info(
            "polling_generation_status",
            task_id=task_id,
            max_wait_seconds=max_wait_seconds
        )

        while True:
            attempt += 1
            elapsed = time.time() - start_time

            if elapsed > max_wait_seconds:
                raise KlingAPIError(
                    f"Video generation timed out after {max_wait_seconds} seconds",
                    task_id=task_id
                )

            try:
                response = requests.get(url, headers=headers, timeout=30)

                if response.status_code != 200:
                    raise KlingAPIError(
                        f"Failed to check status: {response.text}",
                        status_code=response.status_code,
                        task_id=task_id
                    )

                data = response.json()
                task_data = data.get("data", {})
                task_status = task_data.get("task_status")

                self.logger.info(
                    "generation_status_check",
                    task_id=task_id,
                    status=task_status,
                    attempt=attempt,
                    elapsed_seconds=int(elapsed)
                )

                if task_status == "succeed":
                    video_url = task_data.get("task_result", {}).get("videos", [{}])[0].get("url")

                    if not video_url:
                        raise KlingAPIError("No video URL in completed task", task_id=task_id)

                    self.logger.info(
                        "video_generation_completed",
                        task_id=task_id,
                        total_time_seconds=int(elapsed)
                    )

                    return video_url

                elif task_status == "failed":
                    error_msg = task_data.get("task_status_msg", "Unknown error")
                    raise KlingAPIError(
                        f"Video generation failed: {error_msg}",
                        task_id=task_id
                    )

                elif task_status in ["submitted", "processing"]:
                    # Still in progress, continue polling
                    time.sleep(poll_interval)

                else:
                    # Unknown status
                    self.logger.warning(
                        "unknown_task_status",
                        task_id=task_id,
                        status=task_status
                    )
                    time.sleep(poll_interval)

            except requests.RequestException as e:
                log_error(self.logger, e, "video_generator._poll_generation_status")
                # Retry after a delay
                time.sleep(poll_interval)

    def _download_video(self, video_url: str, output_path: str):
        """
        Download the generated video.

        Args:
            video_url: URL of the generated video
            output_path: Local path to save the video

        Raises:
            KlingAPIError: If download fails
        """
        try:
            self.logger.info("downloading_video", url=video_url, output_path=output_path)

            response = requests.get(video_url, stream=True, timeout=120)

            if response.status_code != 200:
                raise KlingAPIError(
                    f"Failed to download video: {response.status_code}",
                    status_code=response.status_code
                )

            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            # Verify file was downloaded
            file_size = Path(output_path).stat().st_size
            if file_size == 0:
                raise KlingAPIError("Downloaded video file is empty")

            self.logger.info(
                "video_downloaded",
                output_path=output_path,
                file_size_mb=round(file_size / (1024 * 1024), 2)
            )

        except requests.RequestException as e:
            log_error(self.logger, e, "video_generator._download_video")
            raise KlingAPIError(f"Failed to download video: {str(e)}")
        except OSError as e:
            log_error(self.logger, e, "video_generator._download_video")
            raise KlingAPIError(f"Failed to save video file: {str(e)}")
