"""Knowledge database schema."""

DOCUMENT_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS `documents` (
    `document_id` BIGINT NOT NULL AUTO_INCREMENT,
    `title` VARCHAR(255) NOT NULL,
    `content_reference` TEXT NOT NULL,
    `source_type` VARCHAR(64) NOT NULL,
    `language` VARCHAR(16) NOT NULL DEFAULT 'vi',
    `version` INT NOT NULL DEFAULT 1,
    `status` VARCHAR(32) NOT NULL DEFAULT 'active',
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (`document_id`),

    INDEX `idx_documents_status` (`status`),
    INDEX `idx_documents_source_type` (`source_type`)
);
""".strip()


DOCUMENT_VERSION_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS `document_versions` (
    `version_id` BIGINT NOT NULL AUTO_INCREMENT,
    `document_id` BIGINT NOT NULL,
    `version_number` INT NOT NULL,
    `content_reference` TEXT NOT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `is_current` BOOLEAN NOT NULL DEFAULT TRUE,

    PRIMARY KEY (`version_id`),

    CONSTRAINT `fk_document_versions_document`
        FOREIGN KEY (`document_id`)
        REFERENCES `documents` (`document_id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    UNIQUE KEY `uq_document_version`
        (`document_id`, `version_number`),

    INDEX `idx_document_versions_document`
        (`document_id`),

    INDEX `idx_document_versions_current`
        (`document_id`, `is_current`)
);
""".strip()


CHUNK_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS `chunks` (
    `chunk_id` BIGINT NOT NULL AUTO_INCREMENT,
    `document_id` BIGINT NOT NULL,
    `version_id` BIGINT NULL,
    `chunk_index` INT NOT NULL,
    `content` TEXT NOT NULL,
    `metadata` JSON NULL,

    PRIMARY KEY (`chunk_id`),

    CONSTRAINT `fk_chunks_document`
        FOREIGN KEY (`document_id`)
        REFERENCES `documents` (`document_id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT `fk_chunks_version`
        FOREIGN KEY (`version_id`)
        REFERENCES `document_versions` (`version_id`)
        ON DELETE SET NULL
        ON UPDATE CASCADE,

    UNIQUE KEY `uq_document_chunk`
        (`document_id`, `version_id`, `chunk_index`),

    INDEX `idx_chunks_document`
        (`document_id`),

    INDEX `idx_chunks_version`
        (`version_id`)
);
""".strip()


KNOWLEDGE_TABLES_UP_SQL = "\n\n".join(
    [
        DOCUMENT_TABLE_SQL,
        DOCUMENT_VERSION_TABLE_SQL,
        CHUNK_TABLE_SQL,
    ]
)


KNOWLEDGE_TABLES_DOWN_SQL = """
DROP TABLE IF EXISTS `chunks`;
DROP TABLE IF EXISTS `document_versions`;
DROP TABLE IF EXISTS `documents`;
""".strip()