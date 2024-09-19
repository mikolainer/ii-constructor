-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Хост: localhost
-- Время создания: Сен 20 2024 г., 01:30
-- Версия сервера: 10.11.6-MariaDB
-- Версия PHP: 8.0.28

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- База данных: `ii_constructor`
--

-- --------------------------------------------------------

--
-- Структура таблицы `projects`
--

CREATE TABLE `projects` (
  `id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `description` varchar(255) NOT NULL DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `states`
--

CREATE TABLE `states` (
  `project_id` int(11) NOT NULL,
  `id` int(11) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `descr` varchar(255) NOT NULL DEFAULT '',
  `answer` varchar(1024) NOT NULL DEFAULT 'текст ответа',
  `required` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `steps`
--

CREATE TABLE `steps` (
  `project_id` int(11) NOT NULL,
  `from_state_id` int(11) DEFAULT NULL,
  `to_state_id` int(11) DEFAULT NULL,
  `vector_name` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `synonyms`
--

CREATE TABLE `synonyms` (
  `project_id` int(11) NOT NULL,
  `group_name` varchar(50) NOT NULL,
  `value` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `vectors`
--

CREATE TABLE `vectors` (
  `project_id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `type` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `vector_types`
--

CREATE TABLE `vector_types` (
  `typename` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;

--
-- Дамп данных таблицы `vector_types`
--

INSERT INTO `vector_types` (`typename`) VALUES
('synonyms_set');

--
-- Индексы сохранённых таблиц
--

--
-- Индексы таблицы `projects`
--
ALTER TABLE `projects`
  ADD PRIMARY KEY (`id`);

--
-- Индексы таблицы `states`
--
ALTER TABLE `states`
  ADD PRIMARY KEY (`id`,`project_id`) USING BTREE,
  ADD KEY `project_id` (`project_id`);

--
-- Индексы таблицы `steps`
--
ALTER TABLE `steps`
  ADD KEY `from_state_id` (`from_state_id`),
  ADD KEY `to_state_id` (`to_state_id`),
  ADD KEY `vector_name` (`vector_name`),
  ADD KEY `project_id` (`project_id`),
  ADD KEY `steps_ibfk_4` (`project_id`,`vector_name`);

--
-- Индексы таблицы `synonyms`
--
ALTER TABLE `synonyms`
  ADD KEY `group_name` (`group_name`),
  ADD KEY `project_id` (`project_id`),
  ADD KEY `synonyms_ibfk_2` (`project_id`,`group_name`);

--
-- Индексы таблицы `vectors`
--
ALTER TABLE `vectors`
  ADD PRIMARY KEY (`name`,`project_id`) USING BTREE,
  ADD KEY `type` (`type`),
  ADD KEY `project_id` (`project_id`);

--
-- Индексы таблицы `vector_types`
--
ALTER TABLE `vector_types`
  ADD PRIMARY KEY (`typename`);

--
-- AUTO_INCREMENT для сохранённых таблиц
--

--
-- AUTO_INCREMENT для таблицы `projects`
--
ALTER TABLE `projects`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `states`
--
ALTER TABLE `states`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Ограничения внешнего ключа сохраненных таблиц
--

--
-- Ограничения внешнего ключа таблицы `states`
--
ALTER TABLE `states`
  ADD CONSTRAINT `states_to_projid` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`);

--
-- Ограничения внешнего ключа таблицы `steps`
--
ALTER TABLE `steps`
  ADD CONSTRAINT `steps_to_fromstateid` FOREIGN KEY (`from_state_id`) REFERENCES `states` (`id`),
  ADD CONSTRAINT `steps_to_tostateid` FOREIGN KEY (`to_state_id`) REFERENCES `states` (`id`),
  ADD CONSTRAINT `steps_to_vectors` FOREIGN KEY (`project_id`,`vector_name`) REFERENCES `vectors` (`project_id`, `name`) ON UPDATE CASCADE;

--
-- Ограничения внешнего ключа таблицы `synonyms`
--
ALTER TABLE `synonyms`
  ADD CONSTRAINT `synonyms_to_vectors` FOREIGN KEY (`project_id`,`group_name`) REFERENCES `vectors` (`project_id`, `name`) ON UPDATE CASCADE;

--
-- Ограничения внешнего ключа таблицы `vectors`
--
ALTER TABLE `vectors`
  ADD CONSTRAINT `vectors_to_project` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`),
  ADD CONSTRAINT `vectors_to_type` FOREIGN KEY (`type`) REFERENCES `vector_types` (`typename`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
