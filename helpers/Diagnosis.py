import time

def timeit(func):
    def wrapper(*args, **kwargs):
        # Den vollen Funktionsnamen erhalten (inklusive Klassennamen)
        class_name = args[0].__class__.__name__ if args else None
        start_time = time.time()  # Startzeit
        result = func(*args, **kwargs)  # Funktion ausführen
        end_time = time.time()  # Endzeit
        # Name der Funktion und der Klasse ausgeben
        if class_name:
            print(f"Funktion {func.__name__} in Klasse {class_name} dauerte {end_time - start_time:.4f} Sekunden")
        else:
            print(f"Funktion {func.__name__} dauerte {end_time - start_time:.4f} Sekunden")
        return result
    return wrapper