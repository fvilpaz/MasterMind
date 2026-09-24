package ex7_Estructuras;

import java.util.HashSet;

public class Set {

    public static void main(String[] args) {

        // Declaración y creación

        HashSet<String> names = new HashSet<String>();
        var numbers = new HashSet<Integer>();

        // Tamaño
        System.out.println(names.size());

        // Añadir elementos
        names.add("Nando");
        names.add("fvilpaz");
        names.add("fervilpaz@gmail.com");
        System.out.println(names.size());

        System.out.println(names);

        numbers.add(1);
        numbers.add(2);
        numbers.add(3);
        System.out.println(numbers);

        // Acceder a los elementos no puede

        // Buscar elementos
        System.out.println(names.contains("Nando"));
        System.out.println(names.contains("fvilpaz"));
        System.out.println(names.contains("cona"));

        // Eliminar elementos
        names.remove("Nando");
        System.out.println(names);
        System.out.println(names.contains("Nando"));
        System.out.println(names.size());

        // Si exisye un hash asociado a un nombre no lo repite. Dice que lo tiene y no lo implementa
        names.add("fvilpaz");
        names.add("fvilpaz");
        System.out.println(names);

        // Conjuntos
        // numbers.addAll(numbers); error
        var countries = new HashSet<String>();
        countries.add("España");
        countries.add("México");
        countries.add("Argentina");
        countries.add("MoureDev");

        names.addAll(countries);
        System.out.println(names);

        names.removeAll(countries);
        System.out.println(names);

        names.retainAll(countries); // retiene elementos comunes
        System.out.println(names);
    }
}
