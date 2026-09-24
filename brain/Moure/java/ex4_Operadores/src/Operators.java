package ex4_Operadores;

public class Operators {

    public static void main(String[] args) {

        // Aritméticos

        System.out.println("\nAritmticos");
        var a = 6;
        var b = 3;

        System.out.println(a + b);
        System.out.println(a - b);
        System.out.println(a * b);
        System.out.println(a / b);
        System.out.println(a % b);

        // Asignación

        System.out.println("\nAsignación");
        a = b;
        System.out.println(a);
        a = b*2;
        System.out.println(a);
        a += 1;
        System.out.println(a);
        a -= 1;
        System.out.println(a);
        a *= 2;
        System.out.println(a);
        a /= 2;
        System.out.println(a);
        a %= 2;

        // Relacionales (comparación)

        System.out.println("\nRelacionales");
        System.out.println(a == b);
        System.out.println(a == 0);
        System.out.println(a != b);
        System.out.println(a != 0);
        System.out.println(a >= b);
        System.out.println(a >= 0);
        System.out.println(a <= b);
        System.out.println(a <= 0);

        // Lógicos

        // And &&
        System.out.println("\nLógicos");
        System.out.println("\n&&");
        System.out.println(true && true);
        System.out.println(true && false);
        System.out.println(false && true);
        System.out.println(false && false);

        System.out.println(3 > 2 && 5 > 2);
        System.out.println(3 > 2 && 5 == 2);

        // || OR
        System.out.println("\n||");
        System.out.println(true || true);
        System.out.println(true || false);
        System.out.println(false || true);
        System.out.println(false || false);

        System.out.println(3 > 2 || 5 > 2);
        System.out.println(3 > 2 || 5 == 2);

        // ! NOT
        System.out.println("\n!");
        System.out.println(!true);
        System.out.println(!false);

        System.out.println(!(3 > 2 || 5 > 2));
        System.out.println(!(3 > 2 || 5 == 2));

        // Unarios

        System.out.println("\nUnarios");
        System.out.println(+b);
        // System.out.println(b+);
        System.out.println(-b);
        // System.out.println(b-);
        System.out.println(++b);
        System.out.println(b++);
        System.out.println(--b);
        System.out.println(b--);


    }
}
