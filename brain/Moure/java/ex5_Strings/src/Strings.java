package ex5_Strings;

public class Strings {
    public static void main(String[] args) {

        // Cadena de texto
        String name = "Fernando";
        var surname = new String(   "Vilas");
        var alias = "NANDO";
        System.out.print("Print: ");
        System.out.print(name);
        System.out.print(surname);

        System.out.print("\nConcatenación: ");
        System.out.print(name + surname);
        System.out.println(" || " + name + "" + surname);

        // Hallar la longitud
        System.out.print("La longitud de la variable name es de ");
        System.out.print(name.length() + " caracteres.\n");

        // Obtener caracter
        System.out.print("Dame el caracter de la posicion 2 del nombre Fernando: ");
        System.out.println(name.charAt(1));

        System.out.print("Dame el último caracter del nombre Fernando : ");
        System.out.println(name.charAt(name.length()-1));

        // Obtener un subcadena
        System.out.println(name.substring(2)); // Empezara en el 2, con lo cual deberia de poner rnando
        System.out.println(name.substring(0, 3)); // Donde empieza y donde acaba
        System.out.println(name.substring(3,8));

        // Transformar cadenas en mayúsculas o minúsculas
        System.out.println(name.toUpperCase());
        System.out.println(alias.toLowerCase());

        // Comprobar si contiene algo
        System.out.println("Hola Java".contains("nando"));
        System.out.println("Hola Java".toUpperCase().contains("AVA"));

        // Trim y replace
        System.out.println("            Hola me llamo Nando               ".trim()); // limpiara esos espacios
        System.out.println("Hola me llamo Fernando".replace(" ","")); // cambia cosas
        System.out.println("Hola me llamo Fernando".replace("Fernando","Nando"));

        // Format
        var age = 42;
        System.out.println(String.format("Hola, %s. Tengo %d años.", name, age));

    }
}
