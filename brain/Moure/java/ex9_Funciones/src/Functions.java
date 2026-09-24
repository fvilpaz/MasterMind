package ex9_Funciones;

import java.util.ArrayList;
import java.util.Arrays;

public class Functions {

    public static void main(String[] args) {

        // Functions
        // Sin parámetro ni retorno
        for (int index = 0; index < 5; index++) {
            sendEmail();
        }
        sendEmail();

        sendEmailToUser("fvilpaz@gmil.com");
        sendEmailToUser("fvilpaz@gmil.com", "Nando");

        var users = new ArrayList<>(Arrays.asList("Fervilpaz@gmail.com", "Fvilpaz@gmail.com"));
        sendEmailToUser(users);

        var state = sendEmailWithState("Fvilpaz@gmail.com");
        System.out.println(state);
        System.out.println(sendEmailWithState(""));
    }

    public static void sendEmail () {
        System.out.println("Se envía el mail");
    }

    // Función con parámetros
    public static void sendEmailToUser (String email) {
        System.out.println("Se envía el mail a " + email);
    }

    // Sobrecarga de funciones
    public static void sendEmailToUser (String email, String name) {
        System.out.println("Se envía el mail a " + name + "(" + email + ")");
    }

    public static void sendEmailToUser (ArrayList<String> emails) {
        for (String email : emails) {
            sendEmailToUser(email);
        }
    }

    // Función con retorno
    public static boolean sendEmailWithState (String email) {

        if (email.isEmpty()) {
            return false;
        }
        System.out.println("mail enviado a " + email);
        return true;
    }

}
