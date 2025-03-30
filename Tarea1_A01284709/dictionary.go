package main

import "fmt"

type Dictionary struct {
	items map[string]string
}

func NewDictionary() *Dictionary {
	return &Dictionary{
		items: make(map[string]string),
	}
}

func (d *Dictionary) Add(key string, value string) {
	d.items[key] = value
}

func (d *Dictionary) Remove(key string) {
	delete(d.items, key)
}

func (d *Dictionary) Get(key string) string {
	return d.items[key]
}

func (d *Dictionary) Contains(key string) bool {
	return d.items[key] != ""
}

func (d *Dictionary) Print() {
	fmt.Print("{")
	first := true
	for key, value := range d.items {
		if !first {
			fmt.Print(", ")
		}
		fmt.Printf("\"%s\":\"%s\"", key, value)
		first = false
	}
	fmt.Println("}")
}
