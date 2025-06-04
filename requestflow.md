```mermaid
sequenceDiagram
    participant Client
    participant OdService

    Note over Client: Begin client-side streaming
    loop stream ImageRequest
        Client->>OdService: ImageRequest (image_file, model)
    end
    Client->>OdService: End stream
    OdService-->>Client: ImageResponse (success, message, process_time, throughput, power, cpu_utilized, memory_utilized)

    Note over Client: After receiving image response

    Client->>OdService: LogEntry (service_name, ip_address, process_time, grpc_response_time, total_response_time, throughput, power, cpu_utilized, memory_utilized)
    OdService-->>Client: LogResponse (success, message)
