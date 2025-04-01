package main

import "fmt"

type Dictionary[K comparable, V any] struct {
	items map[K]V
}

func NewDictionary[K comparable, V any]() *Dictionary[K, V] {
	return &Dictionary[K, V]{
		items: make(map[K]V),
	}
}

func (d *Dictionary[K, V]) Add(key K, value V) {
	d.items[key] = value
}

func (d *Dictionary[K, V]) Remove(key K) {
	delete(d.items, key)
}

func (d *Dictionary[K, V]) Get(key K) V {
	return d.items[key]
}

func (d *Dictionary[K, V]) Contains(key K) bool {
	_, exists := d.items[key]
	return exists
}

func (d *Dictionary[K, V]) Print() {
	fmt.Print("{")
	first := true
	for key, value := range d.items {
		if !first {
			fmt.Print(", ")
		}
		fmt.Printf("%v:%v", key, value)
		first = false
	}
	fmt.Println("}")
}
