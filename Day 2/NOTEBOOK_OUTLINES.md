# Day 2 Notebook Content Outlines

This document outlines the comprehensive content for all Day 2 notebooks in the Databricks training course.

---

## 1. Semantic Modeling with Unity Catalog Metric Views

**Learning Objectives:**
- Create reusable data models in a semantic layer
- Use Databricks Assistant to generate YAML (not manual typing)
- Define metrics, dimensions, and measures
- Implement composability across metrics

**Key Sections:**
1. Understanding Metric Views
   - What are semantic models?
   - Benefits vs traditional approach
   - Architecture overview

2. Using Databricks Assistant (Primary Method)
   - AI-assisted YAML generation
   - Natural language prompts
   - Iterative refinement
   - Examples: "Create metric view for IoT sensors with avg temp, device count"

3. Metric View Components
   - Entities: Mapping to physical tables
   - Measures: Aggregations (AVG, COUNT, SUM)
   - Dimensions: Categorical, time-based, hierarchical
   - Metrics: Business KPIs

4. Composability
   - Building complex metrics from simple ones
   - Cross-entity relationships
   - Reusable definitions

5. Querying Metric Views
   - SQL queries
   - Natural language (Genie)
   - Dashboard integration

**Hands-on Examples:**
- Create IoT sensor metrics view
- Define avg_temperature, device_count, anomaly_rate
- Add factory, model, time dimensions
- Query with SQL and natural language

**References:**
- https://www.databricks.com/resources/demos/tours/governance/metric-views-with-uc
- https://docs.databricks.com/aws/en/metric-views/

---

## 2. Dashboards Deep Dive

**Learning Objectives:**
- Create advanced dashboards with metric views
- Implement parameters and filters
- Manage permissions and sharing
- Schedule and subscribe to dashboards

**Key Sections:**
1. Advanced Dashboard Features
   - Query-based parameters
   - Dynamic filters
   - Filter types (dropdown, date range, multi-select)
   - Parameter passing between queries

2. Data

sets
   - Reusable query datasets
   - Shared across dashboards
   - Performance benefits

3. Permissions and Sharing
   - Dashboard permissions model
   - Share with users/groups
   - Publish vs edit access
   - Embed in external apps

4. Scheduling and Subscriptions
   - Automatic refresh schedules
   - Email subscriptions
   - Slack notifications
   - Conditional alerts

5. Genie Space Integration
   - Connect dashboards to Genie
   - Natural language queries on dashboard data
   - Interactive exploration

**Hands-on Examples:**
- Build multi-page IoT operations dashboard
- Add factory filter parameter
- Create dataset for sensor metrics
- Schedule daily refresh
- Set up email subscriptions

**References:**
- https://docs.databricks.com/aws/en/dashboards/tutorials/query-based-params
- https://docs.databricks.com/aws/en/dashboards/datasets
- https://docs.databricks.com/aws/en/dashboards/share

---

## 3. Genie Deep Dive: Engineering AI Context

**Learning Objectives:**
- Set up Genie Spaces with proper context
- Create knowledge stores
- Implement query parameters
- Define trusted assets
- Optimize for benchmarks

**Key Sections:**
1. Genie Space Setup
   - Creating effective Genie Spaces
   - Table selection strategy
   - Semantic context

2. Knowledge Store
   - Document business context
   - Sample questions and answers
   - Domain terminology
   - Common metrics definitions

3. Query Parameters
   - Pre-defined filters
   - Dynamic date ranges
   - User-specific contexts

4. Trusted Assets
   - Curated tables and views
   - Metric view integration
   - Data quality filters

5. Benchmarks and Quality
   - Test question sets
   - Accuracy measurement
   - Iterative improvement

6. Best Practices
   - Context engineering tips
   - Prompt optimization
   - User training strategies

**Hands-on Examples:**
- Create IoT Analytics Genie Space
- Add knowledge base with domain terms
- Define trusted metric views
- Test with benchmark questions
- Measure and improve accuracy

**References:**
- https://docs.databricks.com/aws/en/genie/set-up
- https://docs.databricks.com/aws/en/genie/knowledge-store
- https://docs.databricks.com/aws/en/genie/best-practices

---

## 4. Agent Bricks: Building GenAI Systems

**Learning Objectives:**
- Build GenAI agents with point-and-click UI
- Create knowledge assistants
- Integrate retrieval augmented generation (RAG)
- Deploy and test agents

**Key Sections:**
1. Agent Bricks Overview
   - What are Agent Bricks?
   - Use cases for IoT domain
   - Architecture

2. Knowledge Assistant
   - Document ingestion
   - Vector search setup
   - Embedding models
   - Retrieval strategies

3. Building Your First Agent
   - UI walkthrough
   - Component selection
   - Configuration
   - Testing

4. Advanced Agent Patterns
   - Multi-step reasoning
   - Tool calling
   - Custom functions
   - Error handling

5. Deployment and Monitoring
   - Serving endpoints
   - Performance monitoring
   - User feedback collection

**Hands-on Examples:**
- Build IoT Troubleshooting Assistant
- Ingest device manuals and logs
- Configure retrieval
- Test queries: "Why is Factory A showing high temps?"
- Deploy and monitor

**References:**
- https://docs.databricks.com/aws/en/generative-ai/agent-bricks/
- https://docs.databricks.com/aws/en/generative-ai/agent-bricks/knowledge-assistant

---

## 5. Orchestration with Databricks Jobs

**Learning Objectives:**
- Schedule and automate data pipelines
- Configure job tasks and dependencies
- Implement triggers (schedule, file arrival, webhook)
- Monitor job runs

**Key Sections:**
1. Jobs Overview
   - Workflows vs Jobs
   - Use cases
   - Architecture

2. Creating Jobs
   - Job quick start
   - Task types (notebook, SQL, Python, JAR, pipeline)
   - Task parameters
   - Cluster configuration

3. Scheduling
   - Cron expressions
   - Time zone handling
   - Trigger types
   - Manual runs

4. File Arrival Triggers
   - Monitor cloud storage
   - Pattern matching
   - Incremental processing
   - Error handling

5. Task Dependencies
   - Linear workflows
   - Parallel execution
   - Conditional logic
   - Task values passing

6. Monitoring and Debugging
   - Job run history
   - Logs and metrics
   - Alerts and notifications
   - Retry policies

**Hands-on Examples:**
- Schedule daily IoT data pipeline
- Create multi-task workflow:
  1. Ingest sensor data
  2. Run quality checks
  3. Update aggregates
  4. Send summary email
- Set up file arrival trigger
- Configure retry on failure

**References:**
- https://docs.databricks.com/aws/en/jobs/
- https://docs.databricks.com/aws/en/jobs/jobs-quickstart
- https://docs.databricks.com/aws/en/jobs/file-arrival-triggers

---

## 6. Version Control Basics and Databricks Asset Bundles

**Learning Objectives:**
- Understand what version control is and why it matters
- Create and work with Git folders in Databricks
- Make changes, commit, push, and pull code
- Use Asset Bundles through the Databricks UI

**Key Sections:**
1. What is Version Control?
   - Why version control matters for data projects
   - What is Git?
   - Basic concepts: repositories, commits, branches
   - How version control helps teams collaborate

2. Getting Started with Git in Databricks
   - What are Databricks Repos?
   - Creating your first Git folder in Databricks
   - Connecting to your Git provider (Azure DevOps)
   - Understanding the Repos UI

3. Making Changes with Git
   - What happens when you edit a notebook?
   - Viewing your changes
   - Committing changes (saving your work)
   - Writing good commit messages
   - Pushing changes to the remote repository

4. Getting Changes from Others
   - What is "pulling"?
   - Updating your workspace with others' changes
   - Understanding sync status
   - What to do when there are conflicts (basic overview)

5. Basic Branching
   - What is a branch?
   - When to use branches
   - Creating a new branch in the UI
   - Switching between branches
   - Merging branches (concept overview)

6. Databricks Asset Bundles (UI-Based)
   - What are Asset Bundles?
   - Why bundle your Databricks assets?
   - Creating a bundle through the workspace UI
   - What gets included (notebooks, jobs, pipelines)
   - Viewing and managing your bundles
   - Sharing bundles across workspaces

**Hands-on Examples:**
- Create a Git folder for your IoT project in Databricks
- Make changes to a notebook and commit them
- Write a descriptive commit message
- Push your changes to Azure DevOps
- Pull changes from a teammate (simulated)
- Create a simple branch for a new feature
- Package your IoT pipeline as an Asset Bundle using the UI
- Explore the bundle structure

**References:**
- https://docs.databricks.com/aws/en/repos/
- https://docs.databricks.com/aws/en/repos/get-started
- https://docs.databricks.com/aws/en/dev-tools/bundles/
- https://git-scm.com/book/en/v2/Getting-Started-What-is-Git%3F

---

## 7. MLflow and Production AI/ML

**Learning Objectives:**
- Track ML experiments with MLflow 3
- Manage model lifecycle
- Register models in Unity Catalog
- Deploy models to production
- Monitor model performance

**Key Sections:**
1. MLflow 3 Overview
   - What's new in MLflow 3
   - Logged Models concept
   - Deployment Jobs
   - Migration from MLflow 2

2. Experiment Tracking
   - Log parameters, metrics, artifacts
   - Organize experiments
   - Compare runs
   - AutoLogging

3. Model Registry with Unity Catalog
   - Register models
   - Model versioning
   - Alias management (Champion, Challenger)
   - Lineage tracking

4. Model Deployment
   - Batch inference
   - Real-time serving
   - Model Serving endpoints
   - A/B testing

5. Production Workflow
   - Training pipeline
   - Evaluation and validation
   - Approval process
   - Deployment job
   - Monitoring

6. MLOps Best Practices
   - Feature stores
   - Model monitoring
   - Drift detection
   - Retraining strategies

**Hands-on Examples:**
- Train defect prediction model
- Track with MLflow 3
- Register in UC Model Registry
- Create deployment job
- Deploy to serving endpoint
- Monitor predictions

**References:**
- https://docs.databricks.com/aws/en/mlflow/
- https://docs.databricks.com/aws/en/mlflow/mlflow-3-install
- https://docs.databricks.com/aws/en/machine-learning/manage-model-lifecycle/
- https://github.com/pedrozanlorensi/e2e-data-project.git

---

## 8. Performance Tuning and Optimization

**Learning Objectives:**
- Analyze query performance with Query Profile
- Implement Delta Lake optimizations
- Use Predictive Optimization
- Apply best practices for Spark performance

**Key Sections:**
1. Query Performance Analysis
   - Query Profile deep dive
   - Identifying bottlenecks
   - Reading execution plans
   - Cost-based optimization

2. Delta Lake Optimizations
   - OPTIMIZE command (compaction)
   - Z-ORDERING
   - Data skipping
   - File statistics

3. Predictive Optimization
   - Automatic optimization
   - Configuration
   - Monitoring

4. Spark Performance Tuning
   - Partitioning strategies
   - Broadcast joins
   - Caching
   - Shuffle optimization

5. Disk Cache
   - Delta cache
   - Use cases
   - Configuration

6. Best Practices
   - Schema design
   - Partition key selection
   - File size management
   - Query optimization patterns

**Hands-on Examples:**
- Analyze slow IoT aggregation query
- Use Query Profile to identify issues
- Apply OPTIMIZE and Z-ORDER
- Enable Predictive Optimization
- Measure performance improvements
- Implement partitioning strategy

**References:**
- https://docs.databricks.com/aws/en/sql/user/queries/query-profile
- https://docs.databricks.com/aws/en/delta/optimize
- https://docs.databricks.com/aws/en/optimizations/predictive-optimization
- https://docs.databricks.com/aws/en/delta/best-practices

---

## 9. Monitor and Govern Databricks Workspaces

**Learning Objectives:**
- Query system tables for observability
- Create governance dashboards
- Monitor billing and usage
- Implement Unity Catalog security

**Key Sections:**
1. System Tables Overview
   - What are system tables?
   - Available schemas
   - Access requirements
   - Note: We'll use synthetic data for training

2. Billing and Cost Analysis
   - Query billing tables
   - Cost allocation by workspace/user/job
   - Usage detail tags
   - Cost optimization insights

3. Usage Monitoring
   - Query execution logs
   - Warehouse usage
   - Notebook activity
   - User patterns

4. Jobs Cost Analysis
   - Job-level cost tracking
   - Cost per run
   - Optimization opportunities

5. Observability Dashboards
   - Account usage dashboard
   - Workspace health metrics
   - Security audit logs
   - Resource utilization

6. Unity Catalog Governance
   - Access control models
   - Privilege management
   - Data lineage
   - Audit logging

7. Security Best Practices
   - User and group management
   - Row-level security
   - Column masking
   - Compliance reporting

**Hands-on Examples:**
- Query synthetic system tables
- Build cost allocation dashboard
- Monitor warehouse usage
- Analyze job costs
- Create security audit report
- Implement row-level security

**Setup Note:**
Since students won't have access to actual system tables, we'll:
1. Create synthetic system tables dataset
2. Apply correct schema from documentation
3. Generate realistic sample data
4. Use this for all exercises

**References:**
- https://docs.databricks.com/aws/en/admin/system-tables/
- https://docs.databricks.com/aws/en/admin/system-tables/billing
- https://docs.databricks.com/aws/en/data-governance/unity-catalog/
- https://github.com/CodyAustinDavis/dbsql_sme/tree/main/Observability%20Dashboards%20and%20DBA%20Resources

---

## Notebook Structure Standards

Each notebook will follow this structure:

1. **Title and Overview**
   - Learning objectives
   - Prerequisites
   - Use case description

2. **Introduction**
   - Why this topic matters
   - Real-world applications
   - Key concepts

3. **Step-by-Step Content**
   - Theory with examples
   - Hands-on exercises
   - Code examples (Python & SQL where applicable)
   - Visualizations and diagrams

4. **Best Practices**
   - Do's and don'ts
   - Common pitfalls
   - Performance tips
   - Security considerations

5. **Complete Example**
   - End-to-end workflow
   - Production-ready patterns
   - Error handling

6. **Summary**
   - Key takeaways
   - Checklist of learned concepts
   - Next steps

7. **References**
   - Documentation links
   - Additional resources
   - Sample repositories

---

## Content Guidelines

**Code Examples:**
- Both Python and SQL where applicable
- Well-commented
- Production-ready patterns
- Error handling included

**Exercises:**
- Progressive difficulty
- Build on IoT dataset
- Real-world scenarios
- Clear success criteria

**Documentation:**
- Clear explanations
- Visual aids (diagrams, flowcharts)
- Tips and warnings
- Best practices highlighted

**References:**
- All official documentation links
- Community resources
- Sample projects
- Video tutorials

---

## Next Steps

After review and approval of this outline:
1. Generate complete notebooks for all 9 topics
2. Ensure consistency across notebooks
3. Add cross-references between related topics
4. Create setup scripts for synthetic data (where needed)
5. Test all code examples
6. Review and refine based on feedback



