# Development Insights

## Initial Requirements & Architecture Planning
Before building anything, it’s important to clearly understand the customer’s needs and KPIs.
Example:

### Cost vs. Quality Trade-offs
- **Budget-Conscious Approach**: 
  - Use serverless architecture (AWS Lambda) for step 1
  - Keep processing lightweight and quick
  - Focus on cost optimization and auto-scaling
  - Suitable for basic video processing needs

- **Quality-Focused Approach**:
  - Use dedicated infrastructure (EC2/Kubernetes)
  - Implement advanced models (e.g., YOLO for object detection)
  - Allow for longer processing times
  - Better for high-quality, detailed video analysis
  - Suitable when accuracy and detail are priorities

## Development Process
- Implement proper Git workflow with feature branches and meaningful commit messages
- Create shared packages between step1 and step2 to reduce code duplication
- Establish clear development, staging, and production environments

## Model Selection
- Typically use OpenAI models, but chose Gemini based on task recommendations
- Selected Gemini 1.5 Flash over Pro for several key reasons:
  - Faster processing for short video clips
  - Lower cost per request
  - Better suited for basic video analysis and highlight extraction
- Note: If deeper analysis or more complex video understanding was needed, would consider switching to Pro for its enhanced capabilities in complex reasoning and longer context understanding

## Security & Infrastructure
- Move all API keys and secrets to cloud-based secret management (AWS Secrets Manager/Vault)
- Implement cloud storage (S3) for video files instead of local storage
- Add proper authentication and rate limiting for API endpoints
- Implement comprehensive error handling and logging

## Error Handling & Monitoring
- Set up centralized logging system
- Implement proper error tracking and alerting
- Add performance monitoring and metrics
- Create dashboards for system health monitoring

## Development Challenges & Lessons Learned

### Initial Over-engineering
- Started with complex approach using multiple ML models (YOLO, etc.)
- Processing time more than doubled due to model loading and inference
- Realized importance of understanding actual highlight requirements
- Solution: Simplified architecture by removing unnecessary models

### Database Integration Issues
- Step 1 and Step 2 containers couldn't communicate due to isolated Docker networks
- Created shared external network (`video-network`) for cross-container communication
- Configured both compose files to use same network with service name resolution
- Added connection health checks and startup orchestration

