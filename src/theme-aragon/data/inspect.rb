# The files we have are quite shitty, and IDs are very noisy
#   - No flag to indicate expense vs income; but we know they are grouped: first income, then expense
#   - Several IDs are duplicated, because null fields are populated with '0'
#
# Because of the latter we can't go through the files and check that id->description is constant
# for all IDs across all the files, since there are duplicates.
#
# What we can do is check (hold on) that description->id is constant. Apart from the fact that 
# a couple of descriptions appear both on the income and expense side.
#
# Then we can generate a mapping table. Run:
#   $ ruby inspect.rb > ../clasificacion_economica.csv
# And then fix it manually... :/

require 'CSV'

descriptions = {}
current_mode = nil

# Go through all the budget files, checking data is (kind of) consistent, as explained above
Dir['*-presupuesto-*.csv'].each do |filename|
  CSV.foreach(filename) do |row|
    # Read the item
    chapter = row[0]
    article = row[1]
    concept = row[2]
    subconcept = row[3]
    description = row[4].strip

    # We need to differentiate expense and income
    if description == 'EconomicaIngresos'
      current_mode = 'I'
      next
    elsif description == 'EconomicaGastos'
      current_mode = 'G'
      next
    end
    id = "#{current_mode}.#{chapter}.#{article}.#{concept}.#{subconcept}"
    description = "#{current_mode}/#{description}" # Couple of descriptions appear on both sides

    # Check if it matches what we had already
    if descriptions[description] == nil
      descriptions[description] = [id, filename]
    else
      old_id = descriptions[description][0]
      old_filename = descriptions[description][1]
      if old_id != id
        puts "CONFLICT:"
        puts "  Had [#{old_filename}] #{old_id} -> '#{description}'"
        puts "  Got [#{filename}] #{id} -> '#{description}'"
      end
    end
  end
end

# Print the result
descriptions.each do |description, metadata|
  id = metadata[0]
  puts [description.split('/'), id.split('.'), metadata[1]].flatten.to_csv
end