package com.island.todoquest.data

data class TodoState(
    var xp: Int = 0,
    val tasks: MutableList<Task> = mutableListOf(),
    val history: MutableList<Task> = mutableListOf()
)
