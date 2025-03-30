package main

import "fmt"

func main() {
	// Test Stack
	fmt.Println("=== Testing Stack Implementation ===")
	stack := &Stack{}
	stack.Push(1)
	stack.Push(2)
	stack.Push(3)
	fmt.Print("Stack after pushing 1,2,3: ")
	stack.Print()
	fmt.Printf("Popped value: %d\n", stack.Pop())
	fmt.Printf("Popped value: %v\n", stack.Pop())
	fmt.Print("Stack after pop: ")
	stack.Print()
	fmt.Printf("Peek value: %d\n", stack.Peek())
	fmt.Printf("Peek value: %v\n", stack.Peek())
	fmt.Printf("Is stack empty?: %v\n", stack.IsEmpty())
	fmt.Printf("Stack size: %d\n", stack.Size())
	fmt.Printf("Stack size: %v\n", stack.Size())
	stack.Clear()
	fmt.Printf("Is stack empty after clear?: %v\n", stack.IsEmpty())

	// Test Queue
	fmt.Println("\n=== Testing Queue Implementation ===")
	queue := &Queue{}
	queue.Enqueue(1)
	queue.Enqueue(2)
	queue.Enqueue(3)
	fmt.Print("Queue after adding 1,2,3: ")
	queue.Print()
	fmt.Printf("Dequeued value: %d\n", queue.Dequeue())
	fmt.Printf("Dequeued value: %v\n", queue.Dequeue())
	fmt.Print("Queue after dequeue: ")
	queue.Print()
	fmt.Printf("Front value: %d\n", queue.Front())
	fmt.Printf("Front value: %v\n", queue.Front())
	fmt.Printf("Is queue empty?: %v\n", queue.IsEmpty())
	fmt.Printf("Queue size: %d\n", queue.Size())
	fmt.Printf("Queue size: %v\n", queue.Size())
	queue.Clear()
	fmt.Printf("Is queue empty?: %v\n", queue.IsEmpty())

	// Test Dictionary
	fmt.Println("\n=== Testing Dictionary Implementation ===")
	dictionary := NewDictionary()
	dictionary.Add("key1", "value1")
	dictionary.Add("key2", "value2")
	dictionary.Add("key3", "value3")
	fmt.Print("Current dictionary contents:")
	dictionary.Print()
	dictionary.Remove("key2")
	fmt.Print("Dictionary after removing key2:")
	dictionary.Print()
	fmt.Printf("Value for key1: %v\n", dictionary.Get("key1"))
	fmt.Printf("key4 exists in dictionary: %v\n", dictionary.Contains("key4"))
}
