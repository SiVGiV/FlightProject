export class Validations {
    static validateEmail(email) {
        return /[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$/.test(email);
    }

    static validatePassword(password) {
        return /(?=^.{8,}$)((?=.*\d)|(?=.*\W+))(?![.\n])(?=.*[A-Z])(?=.*[a-z]).*$/.test(password);
    }

    static validateUsername(username) {
        return /^[a-zA-Z0-9]{3,}$/.test(username);
    }

    static validatePhone(phone) {
        return /^(\+)?([ 0-9-]){10,16}$/.test(phone)
    }

    static validateRequired(value) {
        return value !== undefined && value !== null && value !== '';
    }
}
