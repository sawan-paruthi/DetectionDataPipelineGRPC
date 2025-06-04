```mermaid

classDiagram
    direction LR
    class app {
        image_processed_flag: boolean
        + UploadImage()
        + SendLogEntry()
        + Serve()
    }
        
    note for app "gRPC Entry Point 💻"
    

    class ImageProcessor {
          process_time: float
          avg_power: float
          throughput: float
          cpu_used: float
          memory_used: float
        + process_image()
        + add_logs()
        + get_throughput()
        + get_powerusage()

    }

    class ObjectProcessor {
        model: string
        detector: string
        + load_model()
        + run()
        + get_device()
    }

 
    class LogEntry {
        + add_to_csv()
        + add_user_data()
        + add_server_data()
        + add_service_data()
    }

    note for LogEntry "📀 DataBase"
    note for LogEntry "🧾 CSV entry"

    class Parameters{
        + get_location()
        + get_subnet()
        + get_asn()
    }

    class Detector{
        Yolo, TorchVision, Panns, MiDaS etc. Implementaion
    }

    app <-- ImageProcessor 
    ImageProcessor <-- ObjectProcessor 
    ImageProcessor <-- LogEntry 
    LogEntry <-- Parameters
    ObjectProcessor <-- Detector


