import os
import tempfile
from concurrent import futures

import grpc
from markitdown import MarkItDown

from owlbot import service_pb2
from owlbot import service_pb2_grpc

md_converter = MarkItDown()


class FileConverterServicer(service_pb2_grpc.FileConverterServicer):
    def ConvertFile(self, request, context):
        suffix = os.path.splitext(request.filename)[1]
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(request.content)
            tmp_path = tmp.name

        try:
            result = md_converter.convert(tmp_path)
            markdown_text = result.text_content
        finally:
            os.remove(tmp_path)

        base_name = os.path.splitext(request.filename)[0]
        return service_pb2.FileResponse(
            filename=f"{base_name}.md",
            markdown=markdown_text,
        )


def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[
            ("grpc.max_send_message_length", 50 * 1024 * 1024),
            ("grpc.max_receive_message_length", 50 * 1024 * 1024),
        ],
    )
    service_pb2_grpc.add_FileConverterServicer_to_server(FileConverterServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("Server running on port 50051")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()