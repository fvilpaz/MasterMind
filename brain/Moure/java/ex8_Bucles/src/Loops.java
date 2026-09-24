package ex8_Bucles;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;

public class Loops {

    public static void main(String[] args) {

        // For controlado por contador
        for (int i = 0; i < 5; i++) {
            System.out.println("Hello Java");
        }

        String[] names = {"Fernando", "Vilas", "Paz"};
        for (int index = 0; index < names.length; index++) {
            System.out.println(names[index]);
        }

        // ForEach
        HashSet<Integer> numbers = new HashSet<>();
        numbers.add(1);
        numbers.add(2);
        numbers.add(3);
        numbers.add(4);
        numbers.add(5);

        for (Integer number : numbers) {
            System.out.println(numbers);
        }

        HashMap<String, String> emails = new HashMap<>();
        emails.put("Nando", "Fervilpaz@gmail.com");
        emails.put("fvilpaz", "fvilpaz@gmail.com");

        for (Map.Entry<String, String> email: emails.entrySet()) {
            System.out.println(email);
            System.out.println(email.getValue());
            System.out.println(email.getKey());
        }

        // While
        int index = 0;
        while (index < 5) {
            System.out.println("Hello Java");
            index++;
        }

        index = 0;
        while (index < names.length) {
            System.out.println(names[index]);
            index++;
        }

        index = 0;
        Boolean find = false;
        while (!find) {
            System.out.println(names[index]);
            if(names[index].equals("Fernando")) {
                find = true;
            }
            index++;
        }

        // Do While
        index = 0;
        do {
            System.out.println("Hola Java");
            index++;
        } while (index < 0);

        // Control de bucles

        // break
        for (String name: names) {
            if(name.equals("Fernando")) {
                break;
            }
            System.out.println(name);
        }

        // continue
        for (int i = 0; i < 5; i++) {
            if (i == 3) {
                continue;
            }
            System.out.println(i);
        }
    }
}
