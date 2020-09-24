class Main {
    main() : AUTO_TYPE {
        let x : AUTO_TYPE <- 3 + 2 in
            case x of
                y : Int => out_string("Ok");
                z : Int => x + h;
            esac
    };

    step(p : AUTO_TYPE) : AUTO_TYPE { p.translate(1, 1) };
};

class A inherits B {

};

class B inherits A {

};

class Point {
    x : AUTO_TYPE;
    y : AUTO_TYPE;

    init(n : Int, m : Int) : SELF_TYPE { {
        x <- n;
        y <- m;
        self;
    } };
};