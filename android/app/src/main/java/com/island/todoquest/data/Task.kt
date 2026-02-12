package com.island.todoquest.data

data class Task(
    val id: String,
    var text: String,
    var weight: Int,
    var completed: Boolean = false,
    var completedAt: String? = null
)
