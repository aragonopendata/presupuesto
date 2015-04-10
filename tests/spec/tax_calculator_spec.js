describe("An average tax-payer", function() {
  var calc;
  var averageVATRate = 0.17657172; // Calculated by hand with Excel

  beforeEach(function() {
    calc = new TaxCalculator();
  });

  it("pays no income tax if she has no income", function() {
    expect(calc.getIncomeTaxPaid(0)).toBe(0);
  });

  it("pays nothing up to a certain minimum (3000 euros deduction)", function() {
    expect(calc.getIncomeTaxPaid(6000)).toBe(0);
  });

  it("pays 24.75% in the first bracket", function() {
    expect(calc.getIncomeTaxPaid(14000)).toBe(14000 * 0.2475 - 3000);
  });

  it("pays 52% in the last bracket (100K extra)", function() {
    var taxBefore = calc.getIncomeTaxPaid(1000000);
    var taxAfter = calc.getIncomeTaxPaid(1100000);
    expect(taxAfter-taxBefore).toBe(100000 * 0.52);
  });

  it("pays a fixed amount in excise (tobacco, alcohol...)", function() {
    expect(calc.getExciseTaxPaid().toFixed(2)).toBe('1062.18');
  });

  it("pays no VAT if there's no consumption", function() {
    expect(calc.getVATPaid(0)).toBe(0);
  });

  it("pays a constant % of the amount saved", function() {
    expect(calc.getVATPaid(10000).toFixed(2)).toBe(Number(averageVATRate * 10000).toFixed(2));
    expect(calc.getVATPaid(200).toFixed(2)).toBe(Number(averageVATRate * 200).toFixed(2));
  });

  it("pays total tax made up of VAT, income tax and excise", function() {
    // Results calculated with Excel by hand
    expect(calc.getIncomeTaxPaid(26000).toFixed(2)).toBe("3870.38");
    expect(calc.getVATPaid(26000-3870.38).toFixed(2)).toBe(((26000 - 3870.38) * averageVATRate).toFixed(2)); // 3448.38
    expect(calc.getTaxPaid(26000).total.toFixed(2)).toBe((3870.38 + calc.getExciseTaxPaid() + 3448.38).toFixed(2));
  });
});