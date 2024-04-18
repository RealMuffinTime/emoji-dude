

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

-- set_guilds
CREATE TABLE IF NOT EXISTS `set_guilds` (
  `guild_id` bigint(18) NOT NULL,
  `auto_reaction_bool_enabled` tinyint(1) NOT NULL DEFAULT 0,
  `auto_poll_thread_creation_bool_enabled` tinyint(1) NOT NULL DEFAULT 0,
  `backup_channel_bool_enabled` tinyint(1) NOT NULL DEFAULT 0,
  `backup_channel_role_moderator` BIGINT(18) DEFAULT NULL,
  `clean_bool_enabled` tinyint(1) NOT NULL DEFAULT 1,
  `clear_bool_enabled` tinyint(1) NOT NULL DEFAULT 1,
  `clear_role_moderator` BIGINT(18) DEFAULT NULL,
  `emojis_bool_enabled` tinyint(1) NOT NULL DEFAULT 1,
  `help_ignore_enabled` tinyint(1) NOT NULL DEFAULT 1,
  `help_role_moderator` BIGINT(18) DEFAULT NULL,
  `managed_afk_bool_enabled` tinyint(1) NOT NULL DEFAULT 0,
  `managed_afk_seconds_timeout` BIGINT(18) NOT NULL DEFAULT 300,
  `managed_channel_bool_enabled` tinyint(1) NOT NULL DEFAULT 0,
  `managed_channel_voice_channel_channel` BIGINT(18) DEFAULT NULL,
  `managed_channel_ignore_channels` varchar(512) DEFAULT NULL,
  `managed_channel_ignore_running` tinyint(1) NOT NULL DEFAULT 0,
  `ping_bool_enabled` tinyint(1) NOT NULL DEFAULT 1,
  `screenshare_bool_enabled` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`guild_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



-- set_users
CREATE TABLE IF NOT EXISTS `set_users` (
  `user_id` bigint(18) NOT NULL,
  `delete_commands` tinyint(1) NOT NULL DEFAULT 0,
  `afk_managed` tinyint(1) NOT NULL DEFAULT 0,
  `last_seen` datetime DEFAULT NULL,
  `last_channel` bigint(18) DEFAULT NULL,
  `last_guild` bigint(18) DEFAULT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



-- stat_bot_commands
CREATE TABLE IF NOT EXISTS `stat_bot_commands` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `timestamp` datetime NOT NULL DEFAULT curtime(),
  `command` varchar(50) NOT NULL,
  `status` varchar(50) NOT NULL,
  `user_id` varchar(50) DEFAULT NULL,
  `guild_id` varchar(50) DEFAULT NULL,

  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



-- stat_bot_guilds
CREATE TABLE IF NOT EXISTS `stat_bot_guilds` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `timestamp` datetime NOT NULL DEFAULT curtime(),
  `action` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



-- stat_bot_online
CREATE TABLE IF NOT EXISTS `stat_bot_online` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `startup` datetime NOT NULL,
  `last_heartbeat` datetime NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;



/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
