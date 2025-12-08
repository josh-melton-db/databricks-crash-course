# Day 2: Advanced Analytics & Automation

## Overview

Build on Day 1 foundations with semantic modeling, advanced dashboards, GenAI applications, and workflow automation. Learn to create reusable, production-ready data solutions.

## Prerequisites

✅ Complete [Day 1](../Day%201/) sessions  
✅ [Setup](../setup/) environment with all tables created

## Schedule

| Time | Session | Topics |
|------|---------|--------|
| 8:30 | Semantic Modeling | Data models, metrics, reusable definitions |
| 10:00 | Dashboards Deep Dive | Advanced features, parameters, drill-downs |
| 11:00 | Genie Deep Dive | Custom context, instructions, optimization |
| 12:00 | *Lunch Break* | |
| 1:00 | Agent Bricks | GenAI applications, RAG, agents |
| 2:00 | Orchestration | Workflows, jobs, scheduling |
| 3:00 | CI/CD and DevOps | Asset bundles, automated testing, deployment |

## Session Details

### 7. Semantic Modeling with Unity Catalog Metric Views (8:30-10:00)

**Learning Objectives:**
- Understand semantic layer concepts and benefits
- Create Unity Catalog Metric Views with YAML
- Define metrics, measures, and dimensions
- Query semantic models with SQL and natural language
- Build foundation for dashboards and Genie

**Notebook:** `1 Semantic Modeling with Metric Views.ipynb`

**Approach:**
This session uses a **"follow along"** approach with the [Databricks Metric Views Demo](https://www.databricks.com/resources/demos/tours/governance/metric-views-with-uc?itm_data=demo_center), adapted to your IOT aircraft data.

**Topics Covered:**
- Unity Catalog Metric Views overview
- YAML structure: metrics, dimensions, relationships
- Following the interactive demo with your tables
- Complete example YAML for IOT sensor data
- Querying metric views in SQL and Genie

**Hands-On:**
- Follow the Databricks demo with these tables:
  - `sensor_bronze`, `dim_factories`, `dim_models`, `dim_devices`
- Create metrics: `avg_temperature`, `defect_rate`, `anomaly_rate`
- Define dimensions: factory, model, time hierarchies
- Test queries in SQL and natural language

**Key Concepts:**
- **Semantic Layer**: Single source of truth for metrics
- **Metric Views**: YAML-defined business metrics
- **Composability**: Build complex metrics from simple ones
- **Reusability**: Power dashboards, Genie, and AI agents
- **Consistency**: Everyone uses the same metric definitions

---

### 8. Dashboards Deep Dive (10:00-11:00)

**Learning Objectives:**
- Build advanced dashboards using semantic models
- Implement parameters and filters
- Create drill-down experiences
- Schedule dashboard refreshes

**Notebook:** `08_dashboards_deep_dive.py`

**Topics Covered:**
- Using semantic models in dashboards
- Dashboard parameters (date ranges, filters)
- Linked visualizations and drill-downs
- Custom formatting and styling
- Embedding dashboards
- Scheduled refreshes
- Access controls

**Hands-On:**
- Create executive dashboard using semantic model
- Add date range parameter
- Link factory chart to device detail table
- Create drill-down from summary to device level
- Schedule daily refresh at 6 AM
- Share with "Executives" group

**Dashboard Examples:**
- Executive Summary: KPIs, trends, top issues
- Factory Performance: Compare facilities
- Device Health Monitor: Real-time status
- Quality Analysis: Defect patterns

---

### 9. Genie Deep Dive (11:00-12:00)

**Learning Objectives:**
- Configure Genie for optimal performance
- Write custom instructions and context
- Test and iterate on responses
- Handle complex queries

**Notebook:** `09_genie_deep_dive.py`

**Topics Covered:**
- Genie architecture and capabilities
- Adding data sources (tables, semantic models)
- Writing effective instructions
- Providing business context
- Sample questions and answers
- Monitoring Genie usage
- Troubleshooting common issues

**Hands-On:**
- Create Genie space: "Manufacturing Analytics"
- Add semantic model as data source
- Write instructions about business context
- Add sample questions library
- Test: "Show me factories with defect rates above 5%"
- Test: "What's trending in temperature data this week?"
- Review query logs and optimize

**Best Practices:**
- Provide clear business definitions
- Include example questions
- Use semantic models for consistency
- Set appropriate permissions
- Monitor and improve based on usage

---

### 10. Agent Bricks (1:00-2:00)

**Learning Objectives:**
- Build GenAI applications with Agent Bricks
- Implement retrieval-augmented generation (RAG)
- Create conversational agents
- Deploy and test applications

**Notebook:** `10_agent_bricks.py`

**Topics Covered:**
- Agent Bricks overview
- Application templates
- Vector search and embeddings
- RAG pattern for Q&A
- Agent configuration and tools
- Testing and evaluation
- Deployment to production

**Hands-On:**
- Create "Manufacturing Assistant" agent
- Configure data sources (sensor tables, manuals)
- Implement RAG for document Q&A
- Add tools: query_defects, get_device_status
- Test conversations
- Deploy to endpoint
- Monitor usage and feedback

**Use Cases:**
- Technical support chatbot
- Automated report generation
- Data analyst assistant
- Predictive maintenance advisor

---

### 11. Orchestration (2:00-3:00)

**Learning Objectives:**
- Create and schedule workflows
- Chain multiple tasks
- Handle dependencies and retries
- Monitor job execution

**Notebook:** `11_orchestration.py`

**Topics Covered:**
- Databricks Workflows overview
- Job types (notebooks, Python, SQL, dbt)
- Task dependencies and parameters
- Scheduling (cron, triggers)
- Cluster configuration
- Error handling and notifications
- Job monitoring and debugging

**Hands-On:**
- Create workflow: "Daily ETL Pipeline"
- Add task 1: Ingest new sensor data
- Add task 2: Run transformations (depends on task 1)
- Add task 3: Update gold tables (depends on task 2)
- Configure schedule: daily at 2 AM
- Set up email notifications on failure
- Test run and monitor execution
- Review task lineage

**Workflow Patterns:**
- Sequential: Task A → Task B → Task C
- Parallel: Multiple independent tasks
- Conditional: Branch based on results
- Incremental: Process only new data

---

### 12. CI/CD and DevOps (3:00-4:00)

**Learning Objectives:**
- Implement version control for notebooks
- Create automated testing
- Deploy with asset bundles
- Set up CI/CD pipelines

**Notebook:** `12_cicd_devops.py`

**Topics Covered:**
- Git integration in Databricks
- Asset bundles overview
- Deploying notebooks and jobs
- Environment management (dev/staging/prod)
- Automated testing strategies
- GitHub Actions / Azure DevOps integration
- Rollback procedures

**Hands-On:**
- Connect workspace to Git repository
- Create asset bundle configuration (databricks.yml)
- Define dev, staging, prod targets
- Write unit tests for transformation logic
- Set up GitHub Action for automated deployment
- Deploy to staging environment
- Promote to production
- Implement rollback test

**DevOps Best Practices:**
- Version control all code
- Separate dev/staging/prod environments
- Automated testing before deployment
- Code reviews and approvals
- Monitoring and alerting
- Documentation and runbooks

---

## Day 2 Outcomes

By the end of Day 2, you will have:

✅ Created reusable semantic models  
✅ Built advanced dashboards with drill-downs  
✅ Configured Genie with custom context  
✅ Deployed a GenAI application with Agent Bricks  
✅ Orchestrated multi-task workflows  
✅ Implemented CI/CD for automated deployments  

## Key Concepts

**Semantic Layer:**
- Centralized business logic
- Consistent metrics across org
- Self-service analytics

**Advanced Dashboards:**
- Interactive and parameterized
- Drill-down capabilities
- Scheduled refreshes

**GenAI:**
- Context-aware chatbots
- RAG for knowledge retrieval
- Agent frameworks

**Automation:**
- Scheduled workflows
- Error handling
- CI/CD pipelines

## Day 2 Takeaways

1. **Semantic Models** enable self-service analytics with consistent definitions
2. **Advanced Dashboards** provide rich, interactive experiences
3. **Genie** becomes more powerful with proper context and instructions
4. **Agent Bricks** make GenAI applications accessible
5. **Orchestration** automates repetitive processes
6. **CI/CD** ensures reliable, tested deployments

## Homework (Optional)

1. Add 5 more measures to your semantic model
2. Create a customer-facing dashboard
3. Train Genie on domain-specific terminology
4. Build an agent with custom tools
5. Create a workflow with conditional branching
6. Set up a full CI/CD pipeline for your project

## Next Steps

Proceed to [Day 3](../Day%203/) for production ML, performance tuning, and platform governance!

## Additional Resources

- [Semantic Models Documentation](https://docs.databricks.com/data-modeling/index.html)
- [Lakeview Advanced Features](https://docs.databricks.com/dashboards/lakeview.html)
- [Databricks Genie](https://docs.databricks.com/genie/index.html)
- [Databricks Workflows](https://docs.databricks.com/workflows/index.html)
- [Asset Bundles](https://docs.databricks.com/dev-tools/bundles/index.html)
- [CI/CD Best Practices](https://docs.databricks.com/dev-tools/ci-cd/index.html)
