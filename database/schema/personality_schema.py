"""Personality database schema."""

PERSONALITY_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS `personalities` (
    `personality_id` BIGINT NOT NULL AUTO_INCREMENT,
    `user_id` BIGINT NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `description` TEXT NOT NULL,
    `speaking_style` TEXT NOT NULL,
    `traits` JSON NULL,
    `behaviors` JSON NULL,
    `version` VARCHAR(100) NOT NULL,
    `active` BOOLEAN NOT NULL DEFAULT TRUE,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (`personality_id`),

    CONSTRAINT `fk_personalities_user`
        FOREIGN KEY (`user_id`)
        REFERENCES `users` (`id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    UNIQUE KEY `uq_personalities_user`
        (`user_id`),

    INDEX `idx_personalities_active`
        (`active`)
) ENGINE=InnoDB;
""".strip()


EMOTION_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS `personality_emotions` (
    `emotion_id` BIGINT NOT NULL AUTO_INCREMENT,
    `personality_id` BIGINT NOT NULL,
    `name` VARCHAR(100) NOT NULL,
    `intensity` DOUBLE NOT NULL DEFAULT 0,
    `valence` DOUBLE NOT NULL DEFAULT 0,
    `context` TEXT NOT NULL,

    PRIMARY KEY (`emotion_id`),

    CONSTRAINT `fk_emotions_personality`
        FOREIGN KEY (`personality_id`)
        REFERENCES `personalities`
            (`personality_id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    INDEX `idx_emotions_personality`
        (`personality_id`)
) ENGINE=InnoDB;
""".strip()


MOOD_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS `personality_moods` (
    `mood_id` BIGINT NOT NULL AUTO_INCREMENT,
    `personality_id` BIGINT NOT NULL,
    `state` VARCHAR(100) NOT NULL,
    `intensity` DOUBLE NOT NULL DEFAULT 0,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (`mood_id`),

    CONSTRAINT `fk_moods_personality`
        FOREIGN KEY (`personality_id`)
        REFERENCES `personalities`
            (`personality_id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    INDEX `idx_moods_personality`
        (`personality_id`)
) ENGINE=InnoDB;
""".strip()


RELATIONSHIP_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS `personality_relationships` (
    `relationship_id` BIGINT NOT NULL AUTO_INCREMENT,
    `personality_id` BIGINT NOT NULL,
    `target_user_id` BIGINT NOT NULL,
    `relationship_type` VARCHAR(100) NOT NULL,
    `strength` DOUBLE NOT NULL DEFAULT 0,

    PRIMARY KEY (`relationship_id`),

    CONSTRAINT `fk_relationships_personality`
        FOREIGN KEY (`personality_id`)
        REFERENCES `personalities`
            (`personality_id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT `fk_relationships_target_user`
        FOREIGN KEY (`target_user_id`)
        REFERENCES `users` (`id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    INDEX `idx_relationships_personality`
        (`personality_id`),

    INDEX `idx_relationships_target_user`
        (`target_user_id`)
) ENGINE=InnoDB;
""".strip()


PERSONALITY_TABLES_UP_SQL = "\n\n".join(
    [
        PERSONALITY_TABLE_SQL,
        EMOTION_TABLE_SQL,
        MOOD_TABLE_SQL,
        RELATIONSHIP_TABLE_SQL,
    ]
)


PERSONALITY_TABLES_DOWN_SQL = """
DROP TABLE IF EXISTS `personality_relationships`;
DROP TABLE IF EXISTS `personality_moods`;
DROP TABLE IF EXISTS `personality_emotions`;
DROP TABLE IF EXISTS `personalities`;
""".strip()