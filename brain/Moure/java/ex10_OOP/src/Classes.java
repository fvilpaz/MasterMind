package ex10_OOP;

public class Classes {
    public static void main(String[] args) {

        var person = new Person("Nando", 42);

        //person.name = "Nando";
        //person.age = 42;

        person.sayHello();

        System.out.println("Hello, " + person.name);
        System.out.println("Cuantos años tienes? " + person.age);


    }
}
