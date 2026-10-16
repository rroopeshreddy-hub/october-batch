cpu_hours=int(input("enter number of cpu hours:"))
storage=int(input("enter storage in gb:"))
data_transfer=int(input("enter data transfer in gb:"))
cpu_cost=cpu_hours*5
storage_cost=storage*2
data_transfer_cost=data_transfer*1
total_amount=cpu_cost+storage_cost+data_transfer_cost
if cpu_hours>100:
     print(total_amount+500)
else:
    print(total_amount)



uptime = 97.5
bill = 50000 if uptime >= 99.9
refund = 0
elif uptime >= 98:
refund = bill * 0.10
else:
refund = bill * 0.25
print("Refund Amount:", refund)


