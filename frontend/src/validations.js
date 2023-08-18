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

    static validatePhone(phone) { // I will regret this regex eventually
        /^(?:(?:(\+?972|\(\+?972\)|\+?\(972\))(?:\s|\.|-)?([1-9]\d?))|(0[23489]{1})|(0[57]{1}[0-9]))(?:\s|\.|-)?([^0\D]{1}\d{2}(?:\s|\.|-)?\d{4})$/.test(phone)
    }

    static validateRequired(value) {
        return value !== undefined && value !== null && value !== '';
    }
}
