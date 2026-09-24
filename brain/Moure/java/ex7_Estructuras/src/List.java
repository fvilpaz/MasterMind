package ex7_Estructuras;

import java.util.ArrayList;

public class List {
    public static void main(String[] args) {

        // Declaración y creación

        ArrayList<String> names = new ArrayList<String>();
        var numbers = new ArrayList<Integer>();

        // Añadir elementos
        System.out.println(names.size());
        names.add("Nando");
        names.add("fvilpaz");
        System.out.println(names.size());

        // Acceder a un elemento
        System.out.println(names.getFirst());
        System.out.println(names.getLast());
        System.out.println(names.get(0));

        // Modificar elementos
        names.set(1, "fvilpaz@gmail.com");
        System.out.println(names.getLast());

        // Eliminar elementos
        names.remove(1);
        //System.out.println(names.get(1));
        System.out.println(names.get(0));
        System.out.println(names.getLast());

        // Buscar elementos
        System.out.println(names.contains("fvilpaz"));
        System.out.println(names.contains("Nando"));

        // Limpiar ArrayList
        names.clear();
        System.out.println(names.size());
    }
}
