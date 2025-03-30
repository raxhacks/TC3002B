package main

import "fmt"

type Queue struct {
	items []int
}

func (q *Queue) Enqueue(item int) {
	q.items = append(q.items, item)
}

func (q *Queue) Dequeue() int {
	item := q.items[0]
	q.items = q.items[1:]
	return item
}

func (q *Queue) Front() int {
	return q.items[0]
}

func (q *Queue) IsEmpty() bool {
	return len(q.items) == 0
}

func (q *Queue) Size() int {
	return len(q.items)
}

func (q *Queue) Print() {
	for _, item := range q.items {
		fmt.Print(item, " ")
	}
	fmt.Println()
}

func (q *Queue) Clear() {
	q.items = []int{}
}
