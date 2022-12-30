fn main() -> Result<(), Box<dyn std::error::Error>> {
    tonic_build::compile_protos("proto/post_generation.proto")?;
    tonic_build::compile_protos("proto/page_generation.proto")?;
    Ok(())
}