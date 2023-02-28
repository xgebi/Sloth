fn main() -> Result<(), Box<dyn std::error::Error>> {
    tonic_build::compile_protos("proto/page_generation.proto")?;
    tonic_build::compile_protos("proto/auth_service.proto")?;
    Ok(())
}