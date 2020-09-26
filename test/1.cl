class A {

	f(a: AUTO_TYPE, b: AUTO_TYPE): AUTO_TYPE {
		a + b
	};

	g(): AUTO_TYPE {
		let x : AUTO_TYPE <- 3 + 2 in
			case x of
				y : Int => out_string("Ok");
				z : Int => x + h;
			esac
	};
};