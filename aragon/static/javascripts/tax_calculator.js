function TaxCalculator() {

  this.getIncomeTaxPaid = function(income) {
    // Calcula el impuesto total a pagar en función de los tramos del IRPF
    // Fuente: http://impuestosrenta.com/tablas-irpf/
    var taxBrackets = [
      [0, 0.2],      // [limite inferior del tramo del IRPF, porcentaje a pagar como suma de tramo estatal + tramo autonómico ]
      [12450, 0.25],
      [20200, 0.31],
      [34000, 0.385],
      [60000, 0.45]
    ];
    var taxToPay = 0;
    for (var i=taxBrackets.length-1; i>=0; i--) {
      taxToPay += Math.max(0, income - taxBrackets[i][0]) * taxBrackets[i][1];
      income = Math.min(income, taxBrackets[i][0]);
    }

    // Se asume una desgravaciones media de 3000 euros
    taxToPay = Math.max(0, taxToPay - 3000);

    return taxToPay;
  };

  this.getExciseTaxPaid = function() {
    // Según el informe de la Agencia Tributaria [1], el importe medio en impuestos especiales es:
    //   20500M euros de recaudación (página 212) / 19.3M declaraciones (página 60)
    // [1]: http://www.minhap.gob.es/Documentacion/Publico/Tributos/Memoria%20Tributaria%202010/MAT2010.pdf
    return 20500.0 / 19.3;
  };

  this.getVATPaid = function(savings) {
    // Según el informe de la Agencia Tributaria [1], la proporción del IVA pagado según los distintos
    // tramos es (sobre un total desglosado del 98.3%):
    //  - superreducido (4%): 6.2% (bienes y servicios nacionales) + 0.7% (intra EU)
    //  - reducido (10%): 18.6% + 0.8%
    //  - general (21%): 64.4% + 7.7%
    var superreducido = savings * 0.04 * (0.062 + 0.007) / 0.983;
    var reducido =      savings * 0.10 * (0.186 + 0.008) / 0.983;
    var general =       savings * 0.21 * (0.644 + 0.077) / 0.983;
    return superreducido + reducido + general;
  };

  // Calcula el impuesto final pagado, como suma de impuesto sobre la renta, IVA e impuestos especiales.
  // Se asume un ahorro del 10%
  this.getTaxPaid = function(income) {
    var incomeTax = this.getIncomeTaxPaid(income);
    var savings = income * 0.10;
    var vat = this.getVATPaid(income - incomeTax - savings);
    var excise = this.getExciseTaxPaid();
    var tramo_ca;
    //Cálculo de impuestos autonómicos: tramo_ca = incomeTax * (Tramo autonomico / total del porcentaje a pagar [variable] en irpf) + vat * 0.5 + excise * 0.58
		if (income < 34000){
      tramo_ca = incomeTax * 0.5 + vat * 0.5 + excise * 0.58;
    }
    else if (income < 60000){
    	tramo_ca = incomeTax * 0.4935 + vat * 0.5 + excise * 0.58;
    }
    else{
    	tramo_ca = incomeTax * 0.4778 + vat * 0.5 + excise * 0.58;
    }
    return {
      'total' : incomeTax + vat + excise,
      'tramo_ca' : tramo_ca
      
    };
  };
}
