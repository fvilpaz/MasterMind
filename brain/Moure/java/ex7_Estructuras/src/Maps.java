package ex7_Estructuras;

import java.util.HashMap;

public class Maps {

    public static void main(String[] args) {

        // Declaración y creación
        HashMap<String, String> names = new HashMap<>();
        var numbers = new HashMap<Integer, String>();

        // Tamaño
        System.out.println(names.size());
        names.put("Nando", "nando@gmail.com");
        names.put("fvilpaz", "fvilpaz@gmail");
        System.out.println(names.size());
        System.out.println(names);

        // Acceder a los elementos
        System.out.println(names.get("Nando"));
        System.out.println(names.get("dev"));

        // Verificar elementos
        System.out.println(names.containsKey("Nando"));
        System.out.println(names.containsKey("dev"));
        System.out.println(names.containsValue("fvilpaz"));

        // Eliminar elementos
        System.out.println(names.remove("Nando"));
        System.out.println(names);

        // Limpiar HashMap
        names.clear();
        System.out.println(names);

        // Otras operaciones
        names.put("fvilpaz", "fvilpaz@gmail");
        System.out.println(names);

        names.put("fvilpaz", "fervilpaz@gmail");
        System.out.println(names);

        names.put("Nando", "fvilpaz@gmail");
        System.out.println(names);

        names.replace("fvilpaz", "fervilpaz@gmail");
        System.out.println(names);

        names.putIfAbsent("fvilpaz", "fervilpaz@gmail");
        System.out.println(names);
    }
}
