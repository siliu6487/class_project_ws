import os
import rclpy
from rclpy.node import Node
from perception_interfaces.srv import PerceptionCheck
from perception_module.utils import predict_audio, detect_pen, load_model
import cv2


class PerceptionService(Node):

    def __init__(self):
        super().__init__('perception_service')

        # pre-trained audio model
        model_path = "~/workspace/class_project_ws/src/perception_module/models/audio_model.pkl"
        self.audio_model = load_model(model_path)

        self.srv = self.create_service(
            PerceptionCheck,
            'perception_check',
            self.callback
        )

        self.get_logger().info("Perception service ready.")

    def callback(self, request, response):
        """
        string file_path: path of the saved sensor data from an interaction.
        string mode: data mode. "audio" for shake and listen interaction, "vision" for tilt and see
        ---
        int32 result: 1 means there is water in bottle or pen in cup; 0 means container is empty

        """
        file_path = os.path.abspath(request.file_path)
        mode = request.mode.lower()

        self.get_logger().info(f"Request: {mode} → {file_path}")

        if not os.path.exists(file_path):
            self.get_logger().error("File does not exist!")
            response.result = -1
            return response

        try:
            if mode == "audio":
                result = predict_audio(file_path, self.audio_model)
                response.result = 1 if result == "water" else 0

            elif mode == "vision":
                img = cv2.imread(file_path)

                if img is None:
                    self.get_logger().error("Failed to read image")
                    response.result = -1
                    return response

                pred, area = detect_pen(img)
                self.get_logger().info(f"Vision area: {area:.1f}")

                response.result = 1 if pred else 0

            else:
                self.get_logger().error(f"Unknown data mode: {mode}")
                response.result = -1

        except Exception as e:
            self.get_logger().error(f"Error: {str(e)}")
            response.result = -1

        return response


def main():
    rclpy.init()
    node = PerceptionService()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()