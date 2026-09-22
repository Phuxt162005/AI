"""Agent and Tool database schema."""

AGENT_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS `agents` (
    `agent_id` BIGINT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(255) NOT NULL,
    `description` TEXT NOT NULL,
    `status` VARCHAR(32) NOT NULL DEFAULT 'active',
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (`agent_id`),

    UNIQUE KEY `uq_agents_name` (`name`),
    INDEX `idx_agents_status` (`status`)
);
""".strip()


AGENT_CONFIGURATION_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS `agent_configurations` (
    `agent_id` BIGINT NOT NULL,
    `model_id` VARCHAR(255) NOT NULL,
    `max_steps` INT NOT NULL DEFAULT 10,
    `temperature` DOUBLE NOT NULL DEFAULT 0.7,
    `timeout` INT NOT NULL DEFAULT 60,
    `system_prompt` TEXT NOT NULL,
    `memory_enabled` BOOLEAN NOT NULL DEFAULT TRUE,

    PRIMARY KEY (`agent_id`),

    CONSTRAINT `fk_agent_config_agent`
        FOREIGN KEY (`agent_id`)
        REFERENCES `agents` (`agent_id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
""".strip()


GOAL_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS `agent_goals` (
    `goal_id` BIGINT NOT NULL AUTO_INCREMENT,
    `agent_id` BIGINT NOT NULL,
    `description` TEXT NOT NULL,
    `status` VARCHAR(32) NOT NULL DEFAULT 'pending',
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (`goal_id`),

    CONSTRAINT `fk_agent_goals_agent`
        FOREIGN KEY (`agent_id`)
        REFERENCES `agents` (`agent_id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    INDEX `idx_agent_goals_agent` (`agent_id`),
    INDEX `idx_agent_goals_status` (`status`)
);
""".strip()


TASK_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS `agent_tasks` (
    `task_id` BIGINT NOT NULL AUTO_INCREMENT,
    `agent_id` BIGINT NOT NULL,
    `goal_id` BIGINT NULL,
    `conversation_id` BIGINT NULL,
    `description` TEXT NOT NULL,
    `status` VARCHAR(32) NOT NULL DEFAULT 'pending',
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (`task_id`),

    CONSTRAINT `fk_agent_tasks_agent`
        FOREIGN KEY (`agent_id`)
        REFERENCES `agents` (`agent_id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT `fk_agent_tasks_goal`
        FOREIGN KEY (`goal_id`)
        REFERENCES `agent_goals` (`goal_id`)
        ON DELETE SET NULL
        ON UPDATE CASCADE,

    CONSTRAINT `fk_agent_tasks_conversation`
        FOREIGN KEY (`conversation_id`)
        REFERENCES `conversations` (`id`)
        ON DELETE SET NULL
        ON UPDATE CASCADE,

    INDEX `idx_agent_tasks_agent` (`agent_id`),
    INDEX `idx_agent_tasks_goal` (`goal_id`),
    INDEX `idx_agent_tasks_conversation`
        (`conversation_id`),
    INDEX `idx_agent_tasks_status` (`status`)
);
""".strip()


PLAN_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS `agent_plans` (
    `plan_id` BIGINT NOT NULL AUTO_INCREMENT,
    `task_id` BIGINT NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `status` VARCHAR(32) NOT NULL DEFAULT 'pending',
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (`plan_id`),

    CONSTRAINT `fk_agent_plans_task`
        FOREIGN KEY (`task_id`)
        REFERENCES `agent_tasks` (`task_id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    INDEX `idx_agent_plans_task` (`task_id`)
);
""".strip()


PLAN_STEP_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS `agent_plan_steps` (
    `plan_step_id` BIGINT NOT NULL AUTO_INCREMENT,
    `plan_id` BIGINT NOT NULL,
    `step_index` INT NOT NULL,
    `description` TEXT NOT NULL,
    `tool_id` BIGINT NULL,
    `status` VARCHAR(32) NOT NULL DEFAULT 'pending',

    PRIMARY KEY (`plan_step_id`),

    CONSTRAINT `fk_agent_plan_steps_plan`
        FOREIGN KEY (`plan_id`)
        REFERENCES `agent_plans` (`plan_id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT `fk_agent_plan_steps_tool`
        FOREIGN KEY (`tool_id`)
        REFERENCES `tools` (`tool_id`)
        ON DELETE SET NULL
        ON UPDATE CASCADE,

    UNIQUE KEY `uq_agent_plan_step`
        (`plan_id`, `step_index`),

    INDEX `idx_agent_plan_steps_plan`
        (`plan_id`)
);
""".strip()


TOOL_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS `tools` (
    `tool_id` BIGINT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(255) NOT NULL,
    `description` TEXT NOT NULL,
    `input_schema` JSON NULL,
    `output_schema` JSON NULL,
    `enabled` BOOLEAN NOT NULL DEFAULT TRUE,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (`tool_id`),

    UNIQUE KEY `uq_tools_name` (`name`),
    INDEX `idx_tools_enabled` (`enabled`)
);
""".strip()


AGENT_TOOL_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS `agent_tools` (
    `agent_id` BIGINT NOT NULL,
    `tool_id` BIGINT NOT NULL,
    `enabled` BOOLEAN NOT NULL DEFAULT TRUE,

    PRIMARY KEY (`agent_id`, `tool_id`),

    CONSTRAINT `fk_agent_tools_agent`
        FOREIGN KEY (`agent_id`)
        REFERENCES `agents` (`agent_id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT `fk_agent_tools_tool`
        FOREIGN KEY (`tool_id`)
        REFERENCES `tools` (`tool_id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
""".strip()


EXECUTION_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS `agent_executions` (
    `execution_id` BIGINT NOT NULL AUTO_INCREMENT,
    `task_id` BIGINT NOT NULL,
    `status` VARCHAR(32) NOT NULL DEFAULT 'running',
    `current_step` INT NOT NULL DEFAULT 0,
    `error_message` TEXT NULL,
    `started_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `finished_at` TIMESTAMP NULL,

    PRIMARY KEY (`execution_id`),

    CONSTRAINT `fk_agent_executions_task`
        FOREIGN KEY (`task_id`)
        REFERENCES `agent_tasks` (`task_id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    INDEX `idx_agent_executions_task`
        (`task_id`),
    INDEX `idx_agent_executions_status`
        (`status`)
);
""".strip()


TOOL_CALL_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS `tool_calls` (
    `tool_call_id` BIGINT NOT NULL AUTO_INCREMENT,
    `execution_id` BIGINT NOT NULL,
    `agent_id` BIGINT NOT NULL,
    `task_id` BIGINT NOT NULL,
    `tool_id` BIGINT NOT NULL,
    `input_data` JSON NULL,
    `status` VARCHAR(32) NOT NULL DEFAULT 'pending',
    `attempt` INT NOT NULL DEFAULT 1,
    `error_message` TEXT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `finished_at` TIMESTAMP NULL,

    PRIMARY KEY (`tool_call_id`),

    CONSTRAINT `fk_tool_calls_execution`
        FOREIGN KEY (`execution_id`)
        REFERENCES `agent_executions` (`execution_id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT `fk_tool_calls_agent`
        FOREIGN KEY (`agent_id`)
        REFERENCES `agents` (`agent_id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT `fk_tool_calls_task`
        FOREIGN KEY (`task_id`)
        REFERENCES `agent_tasks` (`task_id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT `fk_tool_calls_tool`
        FOREIGN KEY (`tool_id`)
        REFERENCES `tools` (`tool_id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    INDEX `idx_tool_calls_execution`
        (`execution_id`),
    INDEX `idx_tool_calls_task`
        (`task_id`),
    INDEX `idx_tool_calls_tool`
        (`tool_id`)
);
""".strip()


EXECUTION_RESULT_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS `execution_results` (
    `result_id` BIGINT NOT NULL AUTO_INCREMENT,
    `tool_call_id` BIGINT NOT NULL,
    `success` BOOLEAN NOT NULL,
    `output_data` JSON NULL,
    `error_message` TEXT NULL,
    `duration_ms` BIGINT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (`result_id`),

    CONSTRAINT `fk_execution_results_tool_call`
        FOREIGN KEY (`tool_call_id`)
        REFERENCES `tool_calls` (`tool_call_id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    INDEX `idx_execution_results_tool_call`
        (`tool_call_id`)
);
""".strip()


AGENT_TABLES_UP_SQL = "\n\n".join(
    [
        AGENT_TABLE_SQL,
        AGENT_CONFIGURATION_TABLE_SQL,
        GOAL_TABLE_SQL,
        TOOL_TABLE_SQL,
        AGENT_TOOL_TABLE_SQL,
        TASK_TABLE_SQL,
        PLAN_TABLE_SQL,
        PLAN_STEP_TABLE_SQL,
        EXECUTION_TABLE_SQL,
        TOOL_CALL_TABLE_SQL,
        EXECUTION_RESULT_TABLE_SQL,
    ]
)


AGENT_TABLES_DOWN_SQL = """
DROP TABLE IF EXISTS `execution_results`;
DROP TABLE IF EXISTS `tool_calls`;
DROP TABLE IF EXISTS `agent_executions`;
DROP TABLE IF EXISTS `agent_plan_steps`;
DROP TABLE IF EXISTS `agent_plans`;
DROP TABLE IF EXISTS `agent_tasks`;
DROP TABLE IF EXISTS `agent_tools`;
DROP TABLE IF EXISTS `tools`;
DROP TABLE IF EXISTS `agent_goals`;
DROP TABLE IF EXISTS `agent_configurations`;
DROP TABLE IF EXISTS `agents`;
""".strip()