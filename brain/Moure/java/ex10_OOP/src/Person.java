package ex10_OOP;

public class Person {

    // Atributos
    String name;
    int age;

    // Constructor
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }

    // Métodos
    public void sayHello() {
        System.out.println("Hola, soy " + name + " y tengo " + age + " años.");
    }
}
