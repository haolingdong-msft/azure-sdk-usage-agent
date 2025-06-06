package com.haolingdong.tools;

import org.springframework.ai.tool.annotation.Tool;
import org.springframework.ai.tool.annotation.ToolParam;
import org.springframework.stereotype.Service;

@Service
public class MgmtUsageDataService {

    @Tool(description = "Get usage data for a specific product and an azure service provider during a time period")
    public String getUsageDataForProductAndProvider(
            @ToolParam(description = "product name") String product,
            @ToolParam(description = "azure service provider name") String provider,
            @ToolParam(description = "month of year") String month) {

        return "dddd";
    }

//    @Tool(description = "Get user info by username and age")
//    public String getUserInfo(
//            @ToolParam(description = "product name") String username,
//            @ToolParam(description = "azure service provider name") String age) {
//        return "User: " + username + ", Age: " + age;
//    }

}
