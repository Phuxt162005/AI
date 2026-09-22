"""Avatar database schema."""

AVATAR_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS `avatars` (
    `avatar_id` BIGINT NOT NULL AUTO_INCREMENT,
    `user_id` BIGINT NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `model_reference` TEXT NULL,
    `display_configuration` JSON NULL,
    `status` VARCHAR(32) NOT NULL DEFAULT 'active',
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (`avatar_id`),

    CONSTRAINT `fk_avatars_user`
        FOREIGN KEY (`user_id`)
        REFERENCES `users` (`id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    INDEX `idx_avatars_user`
        (`user_id`)
) ENGINE=InnoDB;
""".strip()


EXPRESSION_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS `avatar_expressions` (
    `expression_id` BIGINT NOT NULL AUTO_INCREMENT,
    `avatar_id` BIGINT NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `emotion` VARCHAR(100) NOT NULL,
    `parameters` JSON NULL,

    PRIMARY KEY (`expression_id`),

    CONSTRAINT `fk_expressions_avatar`
        FOREIGN KEY (`avatar_id`)
        REFERENCES `avatars` (`avatar_id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    INDEX `idx_expressions_avatar`
        (`avatar_id`)
) ENGINE=InnoDB;
""".strip()


ANIMATION_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS `avatar_animations` (
    `animation_id` BIGINT NOT NULL AUTO_INCREMENT,
    `avatar_id` BIGINT NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `intent` VARCHAR(100) NOT NULL,
    `loop` BOOLEAN NOT NULL DEFAULT FALSE,
    `duration_ms` INT NOT NULL DEFAULT 0,
    `transition_ms` INT NOT NULL DEFAULT 0,
    `asset_reference` TEXT NULL,

    PRIMARY KEY (`animation_id`),

    CONSTRAINT `fk_animations_avatar`
        FOREIGN KEY (`avatar_id`)
        REFERENCES `avatars` (`avatar_id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    INDEX `idx_animations_avatar`
        (`avatar_id`)
) ENGINE=InnoDB;
""".strip()


VOICE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS `avatar_voices` (
    `voice_id` BIGINT NOT NULL AUTO_INCREMENT,
    `avatar_id` BIGINT NOT NULL,
    `external_voice_id` VARCHAR(255) NOT NULL,
    `model` VARCHAR(255) NOT NULL,
    `language` VARCHAR(64) NOT NULL,
    `configuration` JSON NULL,
    `speech_parameters` JSON NULL,

    PRIMARY KEY (`voice_id`),

    CONSTRAINT `fk_voices_avatar`
        FOREIGN KEY (`avatar_id`)
        REFERENCES `avatars` (`avatar_id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    INDEX `idx_voices_avatar`
        (`avatar_id`)
) ENGINE=InnoDB;
""".strip()


AUDIO_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS `avatar_audio` (
    `audio_id` BIGINT NOT NULL AUTO_INCREMENT,
    `avatar_id` BIGINT NOT NULL,
    `asset_reference` TEXT NOT NULL,
    `content_type` VARCHAR(100) NOT NULL,
    `duration_ms` INT NOT NULL DEFAULT 0,
    `metadata` JSON NULL,

    PRIMARY KEY (`audio_id`),

    CONSTRAINT `fk_audio_avatar`
        FOREIGN KEY (`avatar_id`)
        REFERENCES `avatars` (`avatar_id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    INDEX `idx_audio_avatar`
        (`avatar_id`)
) ENGINE=InnoDB;
""".strip()


VISUAL_STATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS `avatar_visual_states` (
    `visual_state_id` BIGINT NOT NULL AUTO_INCREMENT,
    `avatar_id` BIGINT NOT NULL,
    `expression_id` BIGINT NULL,
    `animation_id` BIGINT NULL,
    `pose` VARCHAR(100) NOT NULL DEFAULT 'idle',
    `visible` BOOLEAN NOT NULL DEFAULT TRUE,
    `parameters` JSON NULL,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (`visual_state_id`),

    CONSTRAINT `fk_visual_states_avatar`
        FOREIGN KEY (`avatar_id`)
        REFERENCES `avatars` (`avatar_id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT `fk_visual_states_expression`
        FOREIGN KEY (`expression_id`)
        REFERENCES `avatar_expressions`
            (`expression_id`)
        ON DELETE SET NULL
        ON UPDATE CASCADE,

    CONSTRAINT `fk_visual_states_animation`
        FOREIGN KEY (`animation_id`)
        REFERENCES `avatar_animations`
            (`animation_id`)
        ON DELETE SET NULL
        ON UPDATE CASCADE,

    INDEX `idx_visual_states_avatar`
        (`avatar_id`)
) ENGINE=InnoDB;
""".strip()


AVATAR_TABLES_UP_SQL = "\n\n".join(
    [
        AVATAR_TABLE_SQL,
        EXPRESSION_TABLE_SQL,
        ANIMATION_TABLE_SQL,
        VOICE_TABLE_SQL,
        AUDIO_TABLE_SQL,
        VISUAL_STATE_TABLE_SQL,
    ]
)


AVATAR_TABLES_DOWN_SQL = """
DROP TABLE IF EXISTS `avatar_visual_states`;
DROP TABLE IF EXISTS `avatar_audio`;
DROP TABLE IF EXISTS `avatar_voices`;
DROP TABLE IF EXISTS `avatar_animations`;
DROP TABLE IF EXISTS `avatar_expressions`;
DROP TABLE IF EXISTS `avatars`;
""".strip()