# Azure SDK Usage Data Agent


## Why?

Usage data(e.g. mgmt-plane SDK usage data from ARM logs, package release status data, data from Azure SDK plugins etc.) is very important for us to make data-driven decisions during developing new features, deprecating existing features, Track1 to Track2 migration, dependency upgrade etc. It is also very important for us to understand our product's customers and see our product's impact.

## What?
We would like to build an agent for both SDK owners and service team to view their interested data easily. We will start with mgmt-plane SDK usage data first. And in the future more data source can be integrated. The user entry point could be a Teams chatbot, and user can input queries and we will return summary and report/chart. Queries can be: "Summarize the usage of OpenAI management SDK", "What is the Track1 to Track2 migration status for Java SDK", "How many users are using protocol methods?" etc.

## How?
PowerBI provides copilot features, but after investigation, it can't answer general questions like above examples, it can't analyze data from multiple tables or data sources , and it is only available in PowerBI UI. So we decide to use MCP server to query data from different usage data source. And create an agent to call MCP server and return the summary and report.

There are also service team asking to build their own agent or dashboard to view their service's specific data, so we can also open the MCP server to let them access data and build their own agent.

## Why build MCP server instead of using PowerBI copilot?

1. General questions like: summarize Java sdk usage,, you will need to query different tables and return the aggregated result, copilot instruction can't do this
2. Scalability on data source: support query usage data from different data source. Summarize and aggregate the result from different table together. Copilot instruction has limitation on character length, it's hard for it to understand all of our data and do the correct query by using instruction only.
3. Support different user entry points beside pbi UI, e.g. teams agent