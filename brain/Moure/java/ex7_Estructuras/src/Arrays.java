package ex7_Estructuras;

public class Arrays {

    public static void main(String[] args) {

        // Declaración y creación
        int[] numbers = new int[3];
        System.out.println(numbers);

        String[] names = {"Fernando", "Vilas", "Nando"};
        System.out.println(names);

        // Acceso
        System.out.println(names[0]);
        System.out.println(numbers[0]);

        // Modificación
        System.out.println((new String[3])[1]);
        numbers[0] = 1;
        numbers[1] = 2;
        numbers[2] = 3;
        System.out.println(numbers[0]);
        System.out.println(numbers[1]);
        System.out.println(numbers[2]);
        // System.out.println(numbers[3]); eso daria error

        names[0] = "Nando";
        System.out.println(names[0]);
        System.out.println(names.length);
        // Eliminar
        names[2] = null;
        System.out.println(names[2]);
        System.out.println(names.length); // no se puede eliminar datos

        // numbers[2] = null; los int son primitivos, no son compatibles
        boolean[] bools = new boolean[3];
        System.out.println(bools[2]);
    }
}
