function TaxCalculator() {

  this.getIncomeTaxPaid = function(income) {
    // Calcula el impuesto total a pagar en función de los tramos del IRPF
    // fuente impuesto autonómico: https://www.boe.es/ccaa/boa/2015/250/d37686-37762.pdf
    // fuente impuesto nacional: http://boe.es/legislacion/codigos/codigo.php?id=064_Impuesto_sobre_la_Renta_de_las_Personas_Fisicas&modo=1
    var taxBrackets = [
      [0, 0.195],      // [limite inferior del tramo del IRPF, porcentaje a pagar como suma de tramo estatal + tramo autonómico ]
      [12450, 0.245],
      [20200, 0.305],
      [34000, 0.375],
      [50000, 0.395],
      [60000, 0.445],
      [70000, 0.45],
      [90000, 0.46],
      [130000, 0.47],
      [150000, 0.475]
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

    // Cálculo de impuestos autonómicos: tramo_ca = incomeTax * (Tramo autonomico / total del porcentaje a pagar [variable] en irpf) + vat * 0.5 + excise * 0.58
    var tramo_ca;
    if (income < 12450) {
      tramo_ca = incomeTax * 0.5128 + vat * 0.5 + excise * 0.58;
    } else if (income < 20200) {
      tramo_ca = incomeTax * 0.5102 + vat * 0.5 + excise * 0.58;
    } else if (income < 34000) {
      tramo_ca = incomeTax * 0.5082 + vat * 0.5 + excise * 0.58;
    } else if (income < 50000) {
      tramo_ca = incomeTax * 0.5067 + vat * 0.5 + excise * 0.58;
    } else if (income < 60000) {
      tramo_ca = incomeTax * 0.5316 + vat * 0.5 + excise * 0.58;
    } else if (income < 70000) {
      tramo_ca = incomeTax * 0.4944 + vat * 0.5 + excise * 0.58;
    } else if (income < 90000) {
      tramo_ca = incomeTax * 0.5 + vat * 0.5 + excise * 0.58;
    } else if (income < 130000) {
      tramo_ca = incomeTax * 0.5109 + vat * 0.5 + excise * 0.58;
     } else if (income < 150000) {
      tramo_ca = incomeTax * 0.5213 + vat * 0.5 + excise * 0.58;
    } else {
      tramo_ca = incomeTax * 0.5263 + vat * 0.5 + excise * 0.58;
    }
    
    return {
      'total' : incomeTax + vat + excise,
      'tramo_ca' : tramo_ca
    };
  };
}
