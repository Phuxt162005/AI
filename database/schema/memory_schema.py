"""Schema definition for Memory data."""

MEMORY_TABLE = "memories"

MEMORY_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS `memories` (
    `memory_id` BIGINT NOT NULL AUTO_INCREMENT,
    `user_id` BIGINT NOT NULL,
    `memory_type` VARCHAR(32) NOT NULL,
    `content` TEXT NOT NULL,
    `importance` DECIMAL(5,4) NOT NULL DEFAULT 0.5000,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    `expires_at` TIMESTAMP NULL,
    `status` VARCHAR(32) NOT NULL DEFAULT 'active',

    PRIMARY KEY (`memory_id`),

    CONSTRAINT `fk_memories_user`
        FOREIGN KEY (`user_id`)
        REFERENCES `users` (`id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT `chk_memories_importance`
        CHECK (`importance` >= 0.0 AND `importance` <= 1.0),

    INDEX `idx_memories_user`
        (`user_id`),

    INDEX `idx_memories_user_type`
        (`user_id`, `memory_type`),

    INDEX `idx_memories_user_status`
        (`user_id`, `status`),

    INDEX `idx_memories_expiration`
        (`expires_at`),

    INDEX `idx_memories_user_updated`
        (`user_id`, `updated_at`)
);
""".strip()

MEMORY_TABLE_DROP_SQL = """
DROP TABLE IF EXISTS `memories`;
""".strip()