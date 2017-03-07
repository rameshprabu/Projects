use trip_advicer

select sum(food_senti) as food_senti,sum(service_senti) as service_senti,sum(resta_senti) as restaurant_senti,sum(price_senti) as price_senti,sum(room_senti) as room_senti,sum(subject_senti) as subjet_senti,country from hotel_senti_rating group by country order by food_senti desc;
select sum(food_senti) as food_senti,sum(service_senti) as service_senti,sum(resta_senti) as restaurant_senti,sum(price_senti) as price_senti,sum(room_senti) as room_senti,sum(subject_senti) as subjet_senti,month_year from hotel_senti_rating group by month_year order by food_senti desc;