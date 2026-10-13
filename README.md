English Practice Bot

A Telegram bot for practising spoken English with AI-powered feedback.

Overview

English Practice Bot helps users improve their English by sending voice messages in English through Telegram.

The bot transcribes each voice message into text and sends it to a language model, which identifies mistakes and provides corrections and feedback.

The bot also tracks the topics users have already practised, helping it avoid repeatedly generating lessons on the same topics.

Features
Voice message transcription — converts spoken English into text.
AI-powered feedback — identifies language mistakes and provides corrections.
Personalised practice — takes previously practised topics into account when generating new lessons.
Learning progress tracking — stores user-related learning data in a database.
Tech Stack
Python
aiogram — Telegram bot framework
SQLAlchemy — database ORM
PostgreSQL — database
Alembic — database migrations

Future Improvements

The ability to track progress over time will be added.
There are plans to add the ability to engage in full-fledged conversation with the neural network—one that remembers context while continuing to perform the role of a teacher.
