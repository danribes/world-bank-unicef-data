#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

const UNICEF_API_BASE = "https://sdmx.data.unicef.org/ws/public/sdmxapi/rest";

// Key UNICEF dataflows with child-related data
const DATAFLOWS = {
  CHLD_PVTY: "Child Poverty",
  CME: "Child Mortality Estimates",
  NUTRITION: "Nutrition",
  IMMUNIZATION: "Immunization",
  EDUCATION: "Education",
  WATER_SANITATION: "Water and Sanitation",
  CHILD_PROTECTION: "Child Protection",
  HIV_AIDS: "HIV/AIDS",
  ADOLESCENT: "Adolescent",
  ECD: "Early Childhood Development",
  GLOBAL_DATAFLOW: "Global Dataflow (all indicators)",
};

// Common indicators
const INDICATORS = {
  // Child Poverty
  "PT_CHLD_Y0-17_MDP": "Children in multidimensional poverty (%)",
  "PT_CHLD_Y0-17_ADMP": "Average deprivations among poor children",
  "PV_CHLD_DDAY-2017": "Children living below $2.15/day (%)",
  "PV_CHLD_LMIC-2017": "Children living below $3.65/day (%)",
  "PV_CHLD_UMIC-2017": "Children living below $6.85/day (%)",
  "PV_VMIR": "Vast Majority Income Ratio",

  // Child Mortality
  "CME_MRY0": "Under-five mortality rate",
  "CME_MRY0T4": "Infant mortality rate",
  "CME_MRM0": "Neonatal mortality rate",

  // Nutrition
  "NT_BW_LBW": "Low birthweight (%)",
  "NT_ANT_WHZ_NE2": "Wasting prevalence (%)",
  "NT_ANT_HAZ_NE2": "Stunting prevalence (%)",
  "NT_ANT_WHZ_PO2": "Overweight prevalence (%)",
};

class UnicefServer {
  constructor() {
    this.server = new Server(
      {
        name: "unicef-mcp-server",
        version: "1.0.0",
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupToolHandlers();
  }

  setupToolHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: "list_dataflows",
          description: "List all available UNICEF dataflows (datasets)",
          inputSchema: {
            type: "object",
            properties: {},
          },
        },
        {
          name: "get_indicators",
          description: "Get available indicators for a specific dataflow",
          inputSchema: {
            type: "object",
            properties: {
              dataflow_id: {
                type: "string",
                description: "The dataflow ID (e.g., CHLD_PVTY, CME, NUTRITION)",
              },
            },
            required: ["dataflow_id"],
          },
        },
        {
          name: "get_child_poverty_data",
          description: "Get child poverty indicators for a specific country",
          inputSchema: {
            type: "object",
            properties: {
              country_code: {
                type: "string",
                description: "ISO3 country code (e.g., USA, BRA, IND)",
              },
              start_year: {
                type: "integer",
                description: "Start year for data (optional)",
              },
              end_year: {
                type: "integer",
                description: "End year for data (optional)",
              },
            },
            required: ["country_code"],
          },
        },
        {
          name: "get_child_mortality_data",
          description: "Get child mortality indicators for a specific country",
          inputSchema: {
            type: "object",
            properties: {
              country_code: {
                type: "string",
                description: "ISO3 country code (e.g., USA, BRA, IND)",
              },
              start_year: {
                type: "integer",
                description: "Start year for data (optional)",
              },
              end_year: {
                type: "integer",
                description: "End year for data (optional)",
              },
            },
            required: ["country_code"],
          },
        },
        {
          name: "get_nutrition_data",
          description: "Get child nutrition indicators for a specific country",
          inputSchema: {
            type: "object",
            properties: {
              country_code: {
                type: "string",
                description: "ISO3 country code (e.g., USA, BRA, IND)",
              },
              start_year: {
                type: "integer",
                description: "Start year for data (optional)",
              },
              end_year: {
                type: "integer",
                description: "End year for data (optional)",
              },
            },
            required: ["country_code"],
          },
        },
        {
          name: "get_indicator_for_country",
          description: "Get a specific indicator for a country from any dataflow",
          inputSchema: {
            type: "object",
            properties: {
              dataflow_id: {
                type: "string",
                description: "The dataflow ID (e.g., CHLD_PVTY, CME, GLOBAL_DATAFLOW)",
              },
              country_code: {
                type: "string",
                description: "ISO3 country code (e.g., USA, BRA, IND)",
              },
              indicator_id: {
                type: "string",
                description: "The indicator ID (optional, returns all if not specified)",
              },
              start_year: {
                type: "integer",
                description: "Start year for data (optional)",
              },
              end_year: {
                type: "integer",
                description: "End year for data (optional)",
              },
            },
            required: ["dataflow_id", "country_code"],
          },
        },
        {
          name: "search_indicators",
          description: "Search for indicators by keyword",
          inputSchema: {
            type: "object",
            properties: {
              keyword: {
                type: "string",
                description: "Keyword to search for (e.g., 'poverty', 'mortality', 'nutrition')",
              },
            },
            required: ["keyword"],
          },
        },
      ],
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case "list_dataflows":
            return await this.listDataflows();
          case "get_indicators":
            return await this.getIndicators(args.dataflow_id);
          case "get_child_poverty_data":
            return await this.getData("CHLD_PVTY", args.country_code, null, args.start_year, args.end_year);
          case "get_child_mortality_data":
            return await this.getData("CME", args.country_code, null, args.start_year, args.end_year);
          case "get_nutrition_data":
            return await this.getData("NUTRITION", args.country_code, null, args.start_year, args.end_year);
          case "get_indicator_for_country":
            return await this.getData(args.dataflow_id, args.country_code, args.indicator_id, args.start_year, args.end_year);
          case "search_indicators":
            return await this.searchIndicators(args.keyword);
          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error) {
        return {
          content: [
            {
              type: "text",
              text: `Error: ${error.message}`,
            },
          ],
        };
      }
    });
  }

  async listDataflows() {
    try {
      const response = await fetch(
        `${UNICEF_API_BASE}/dataflow/all/all/latest/?format=sdmx-json&detail=allstubs`
      );
      const data = await response.json();

      const dataflows = data.data?.dataflows || [];
      const result = dataflows.map(df => ({
        id: df.id,
        name: df.names?.en || df.name || "Unknown",
        agency: df.agencyID,
      }));

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(result, null, 2),
          },
        ],
      };
    } catch (error) {
      throw new Error(`Failed to fetch dataflows: ${error.message}`);
    }
  }

  async getIndicators(dataflowId) {
    try {
      const response = await fetch(
        `${UNICEF_API_BASE}/dataflow/UNICEF/${dataflowId}/latest/?format=sdmx-json&detail=full&references=all`
      );
      const data = await response.json();

      // Extract indicator codelist
      const codelists = data.data?.codelists || [];
      const indicatorCodelist = codelists.find(cl =>
        cl.id?.includes("INDICATOR") || cl.id?.includes("IND")
      );

      if (!indicatorCodelist) {
        return {
          content: [
            {
              type: "text",
              text: `No indicator codelist found for dataflow ${dataflowId}. Available codelists: ${codelists.map(c => c.id).join(", ")}`,
            },
          ],
        };
      }

      const indicators = indicatorCodelist.codes?.map(code => ({
        id: code.id,
        name: code.names?.en || code.name || "Unknown",
      })) || [];

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(indicators.slice(0, 100), null, 2), // Limit to 100
          },
        ],
      };
    } catch (error) {
      throw new Error(`Failed to fetch indicators: ${error.message}`);
    }
  }

  async getData(dataflowId, countryCode, indicatorId, startYear, endYear) {
    try {
      // Build the data key
      let dataKey = `${countryCode}`;
      if (indicatorId) {
        dataKey += `.${indicatorId}`;
      } else {
        dataKey += ".";
      }

      let url = `${UNICEF_API_BASE}/data/UNICEF,${dataflowId},1.0/${dataKey}?format=csv`;

      if (startYear) {
        url += `&startPeriod=${startYear}`;
      }
      if (endYear) {
        url += `&endPeriod=${endYear}`;
      }

      const response = await fetch(url);
      const csvText = await response.text();

      if (!csvText || csvText.trim() === "") {
        return {
          content: [
            {
              type: "text",
              text: `No data found for ${countryCode} in ${dataflowId}`,
            },
          ],
        };
      }

      return {
        content: [
          {
            type: "text",
            text: csvText,
          },
        ],
      };
    } catch (error) {
      throw new Error(`Failed to fetch data: ${error.message}`);
    }
  }

  async searchIndicators(keyword) {
    try {
      // Search through the global dataflow
      const response = await fetch(
        `${UNICEF_API_BASE}/dataflow/UNICEF/GLOBAL_DATAFLOW/latest/?format=sdmx-json&detail=full&references=all`
      );
      const data = await response.json();

      const codelists = data.data?.codelists || [];
      const indicatorCodelist = codelists.find(cl =>
        cl.id?.includes("INDICATOR") || cl.id?.includes("IND")
      );

      if (!indicatorCodelist) {
        return {
          content: [
            {
              type: "text",
              text: "Could not find indicator codelist",
            },
          ],
        };
      }

      const keywordLower = keyword.toLowerCase();
      const matchingIndicators = indicatorCodelist.codes?.filter(code => {
        const name = (code.names?.en || code.name || "").toLowerCase();
        const id = (code.id || "").toLowerCase();
        return name.includes(keywordLower) || id.includes(keywordLower);
      }).map(code => ({
        id: code.id,
        name: code.names?.en || code.name || "Unknown",
      })) || [];

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(matchingIndicators.slice(0, 50), null, 2),
          },
        ],
      };
    } catch (error) {
      throw new Error(`Failed to search indicators: ${error.message}`);
    }
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error("UNICEF MCP Server running on stdio");
  }
}

const server = new UnicefServer();
server.run().catch(console.error);
