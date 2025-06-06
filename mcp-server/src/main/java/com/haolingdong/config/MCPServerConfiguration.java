package com.haolingdong.config;


import com.haolingdong.tools.MgmtUsageDataService;
import org.springframework.ai.tool.ToolCallback;
import org.springframework.ai.tool.ToolCallbacks;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.List;

@Configuration
public class MCPServerConfiguration {

    @Bean
    public ToolCallbackProvider mgmtUsageDataTools(MgmtUsageDataService mgmtUsageDataService) {
        return  MethodToolCallbackProvider.builder().toolObjects(mgmtUsageDataService).build();
    }
}
