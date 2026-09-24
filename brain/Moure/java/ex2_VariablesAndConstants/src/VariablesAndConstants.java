package ex2_VariablesAndConstants;

public class VariablesAndConstants {

    public static void main(String[] args) {

        // Variables

        String name = "Fernando";
        System.out.println("1_Mi nombre es " + name);
        System.out.print("2_Mi nombre es ");
        System.out.print(name);
        System.out.print("\n");
        System.out.printf("3_Mi nombre es %s\n", name);

        name = "Nando";
        System.out.println("Pero puedes llamarme " + name);

        char initial = 'N';
        System.out.println("Mi inicial es: " + initial);

        // name = 37 no funcionaria porque es un int. "37" eso si lo haría

        int age = 42;
        System.out.println("Tengo " + age + " años");

        var email = "fvilpaz@gmail.com";
        System.out.println("Mi correo es " + email);

        var year = 1984;
        System.out.println("Nací en " + year);

        // Constantes

        final String EMAIL = "fervilpaz@gmail.com";
        // Ahora el mail es constante
        System.out.println("Mi correo ahora es constamte y ha cambiado a " + EMAIL);

        boolean likeProgramming = true;
        System.out.println("¿Me gusta programar? " + likeProgramming);
    }
}
