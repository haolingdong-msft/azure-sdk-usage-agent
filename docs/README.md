# adfSDK - Azure Data Factory SDK (Refactored)

现代化的 Azure Data Factory Python SDK，提供类型安全、完善的日志和错误处理。

## 📁 目录结构

```
adfSDK/
├── __init__.py          # 包入口，导出公共 API
├── __version__.py       # 版本信息
├── client.py            # 主客户端类 ADFClientSDK (~400 行)
├── operations.py        # 底层操作实现 (~350 行)
├── models.py            # 数据模型和类型定义 (~100 行)
├── exceptions.py        # 异常体系 (~160 行)
├── config.py            # 配置管理 (~200 行)
├── utils.py             # 工具函数 (~320 行)
├── py.typed             # PEP 561 类型标记
├── examples/            # 使用示例
│   ├── kusto_query_parameter.py
│   └── kusto_query_usage.py
└── test/                # 测试数据
    └── snapshots/
```

## ✨ 主要改进

### 1. 类型安全
- 使用 `TypedDict` 和 `Enum` 定义数据类型
- 完整的类型注解
- 支持 IDE 自动补全

### 2. 异常体系
- 细粒度的异常类型（`PipelineTimeoutError`, `PipelineTriggerError` 等）
- 携带详细的错误上下文
- 便于精确捕获和处理错误

### 3. 日志系统
- 使用标准 `logging` 模块
- 支持日志级别控制
- 支持文本和 JSON 格式

### 4. 配置管理
- 独立的配置类 `ADFSDKConfig`
- 支持环境变量
- 配置验证

### 5. 工具函数
- 时间处理工具
- 重试装饰器
- 参数验证
- JSON 序列化

## 🚀 快速开始

### 基础用法

```python
from adfSDK import ADFClientSDK

# 方式 1: 直接指定参数
client = ADFClientSDK(
    subscription_id="your-subscription-id",
    resource_group_name="your-rg",
    factory_name="your-factory"
)

# 触发 pipeline
run_id = client.trigger_pipeline("my-pipeline")

# 获取状态
status = client.get_pipeline_run_status(run_id)
print(f"Status: {status['status']}")

# 等待完成
result = client.wait_for_pipeline(run_id)
```

### 使用环境变量

```python
from adfSDK import ADFClientSDK

# 方式 2: 从环境变量加载
# 需要设置: AZURE_SUBSCRIPTION_ID, AZURE_RESOURCE_GROUP, AZURE_FACTORY_NAME
client = ADFClientSDK.from_environment()

# 触发并等待
result = client.run_pipeline("my-pipeline", wait=True)
```

### 使用 Context Manager

```python
from adfSDK import ADFClientSDK

with ADFClientSDK.from_environment() as client:
    # 触发 pipeline
    run_id = client.trigger_pipeline("my-pipeline", parameters={"date": "2024-01-01"})
    
    # 等待完成
    result = client.wait_for_pipeline(run_id)
    
    # 获取 activity runs
    activities = client.get_activity_runs(
        run_id=run_id,
        start_time="2024-01-01T00:00:00Z",
        end_time="2024-01-02T00:00:00Z"
    )
```

### 使用配置对象

```python
from adfSDK import ADFClientSDK, ADFSDKConfig

# 创建配置
config = ADFSDKConfig(
    subscription_id="your-subscription-id",
    resource_group_name="your-rg",
    factory_name="your-factory",
    poll_interval=60,  # 60秒检查一次
    timeout=7200,      # 2小时超时
    log_level="DEBUG",
    auto_save_results=True
)

# 使用配置创建客户端
client = ADFClientSDK.from_config(config)
```

### 错误处理

```python
from adfSDK import ADFClientSDK, PipelineTimeoutError, PipelineTriggerError

client = ADFClientSDK.from_environment()

try:
    run_id = client.trigger_pipeline("my-pipeline")
    result = client.wait_for_pipeline(run_id, timeout=1800)
    
    if result['status'] == 'Succeeded':
        print("Pipeline succeeded!")
    else:
        print(f"Pipeline failed: {result.get('message')}")
        
except PipelineTriggerError as e:
    print(f"Failed to trigger pipeline: {e.message}")
    print(f"Details: {e.details}")
    
except PipelineTimeoutError as e:
    print(f"Pipeline timed out after {e.elapsed}s (limit: {e.timeout}s)")
    print(f"Run ID: {e.run_id}")
```

## 📊 类型支持

### 枚举类型

```python
from adfSDK import RunStatus, ActivityType

# Run 状态
RunStatus.QUEUED
RunStatus.IN_PROGRESS
RunStatus.SUCCEEDED
RunStatus.FAILED
RunStatus.CANCELLED

# Activity 类型
ActivityType.COPY
ActivityType.EXECUTE_PIPELINE
ActivityType.WEB
# ...
```

### 辅助函数

```python
from adfSDK import is_terminal_status, is_successful_status

status = "Succeeded"

if is_terminal_status(status):
    print("Pipeline has completed")

if is_successful_status(status):
    print("Pipeline succeeded!")
```

## ⚙️ 配置选项

### 环境变量

```bash
# 必需
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
export AZURE_RESOURCE_GROUP="your-rg"
export AZURE_FACTORY_NAME="your-factory"

# 可选
export ADF_POLL_INTERVAL=30          # 轮询间隔（秒）
export ADF_TIMEOUT=3600              # 超时时间（秒）
export ADF_LOG_LEVEL=INFO            # 日志级别
export ADF_LOG_FORMAT=text           # 日志格式（text/json）
export ADF_AUTO_SAVE=true            # 自动保存结果
export ADF_OUTPUT_DIR=./output       # 输出目录
```

### 配置类属性

```python
@dataclass
class ADFSDKConfig:
    subscription_id: str
    resource_group_name: str
    factory_name: str
    poll_interval: int = 30
    timeout: int = 3600
    log_level: str = "INFO"
    log_format: str = "text"
    auto_save_results: bool = False
    output_dir: Path = Path("output")
```

## 🔧 高级功能

### 自定义日志

```python
from adfSDK.utils import setup_logging

# 设置日志
setup_logging(level="DEBUG", log_format="json")

# 使用客户端
client = ADFClientSDK.from_environment()
```

## 📝 示例代码

查看 `examples/` 目录获取更多示例：
- `kusto_query_parameter.py` - 参数化查询示例
- `kusto_query_usage.py` - 基础使用示例

## 🔄 迁移指南

### 从旧版本迁移

**旧代码 (v0.1.x):**
```python
from adfSDK import ADFClientSDK

client = ADFClientSDK(subscription_id, resource_group, factory_name)
run_id = client.trigger_pipeline("pipeline")
status = client.get_pipeline_run_status(run_id)
```

**新代码 (v0.2.x):**
```python
from adfSDK import ADFClientSDK, PipelineTimeoutError

# 完全兼容，无需修改！
client = ADFClientSDK(subscription_id, resource_group, factory_name)
run_id = client.trigger_pipeline("pipeline")
status = client.get_pipeline_run_status(run_id)

# 新增功能：使用异常处理
try:
    result = client.wait_for_pipeline(run_id)
except PipelineTimeoutError as e:
    print(f"Timeout: {e}")
```

**主要变更:**
1. ✅ 保持向后兼容 - 旧代码无需修改即可运行
2. ✅ 新增类型定义 - 更好的 IDE 支持
3. ✅ 新增异常类型 - 更精确的错误处理
4. ✅ 新增配置管理 - 更灵活的配置方式
5. ✅ 改进日志 - 使用标准 logging 模块

## 📚 API 文档

### ADFClientSDK

主客户端类，提供所有 ADF 操作。

**方法:**
- `__init__(subscription_id, resource_group_name, factory_name, credential=None, config=None)`
- `from_environment(credential=None)` - 从环境变量创建
- `from_config(config, credential=None)` - 从配置对象创建
- `trigger_pipeline(pipeline_name, parameters=None)` - 触发 pipeline
- `get_pipeline_run_status(run_id)` - 获取状态
- `wait_for_pipeline(run_id, poll_interval=None, timeout=None)` - 等待完成
- `get_activity_runs(run_id, start_time, end_time, save_to_file=None)` - 获取 activity runs
- `run_pipeline(pipeline_name, parameters=None, wait=True, ...)` - 触发并等待
- `close()` - 关闭客户端

### 异常类型

- `ADFError` - 所有异常的基类
- `PipelineError` - Pipeline 相关错误
  - `PipelineNotFoundError` - Pipeline 不存在
  - `PipelineTimeoutError` - 超时
  - `PipelineTriggerError` - 触发失败
  - `PipelineExecutionError` - 执行失败
- `ActivityError` - Activity 相关错误
  - `ActivityRunNotFoundError` - Activity run 不存在
  - `ActivityQueryError` - 查询失败
- `AuthenticationError` - 认证失败
- `ConfigurationError` - 配置错误

## 🛠️ 开发

### 代码结构

- **client.py**: 高层 API，用户直接使用
- **operations.py**: 底层操作，由 client 调用
- **models.py**: 类型定义和枚举
- **exceptions.py**: 异常类型
- **config.py**: 配置管理
- **utils.py**: 工具函数

### 设计原则

1. **单一职责**: 每个模块专注一个功能
2. **类型安全**: 使用类型注解和类型定义
3. **向后兼容**: 保持与旧版本的兼容性
4. **可测试性**: 便于编写单元测试
5. **可扩展性**: 易于添加新功能

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**版本**: 0.2.0  
**更新日期**: 2025-12-16
