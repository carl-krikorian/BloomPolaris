from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from .models import Guest, Manager, Table, MenuItem, Restaurant, Visit, Reservation, Friendship, ReservedTables, Gadget, \
    Transaction, Game, Events, Opportunities, Apply
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils import timezone
from datetime import datetime as dt
import datetime
import pytz
from django.db import transaction
from dateutil import parser
from django.db.models.query import QuerySet


# Homepage
def index(request):
    return render(request, 'Booking/new/index.html')


def homer(request):
    return render(request, 'Booking/new/home.html')


# User login
def login(request):
    if request.method == 'POST':
        # collecting form data
        username = request.POST.get('username')
        password = request.POST.get('password')
        # checking for user first
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                # check if it is quest or manager
                # search for guest
                guest = Guest.objects.all()
                for g in guest:
                    if g.user == user:
                        auth_login(request, user)
                        return HttpResponseRedirect(reverse('Booking:guest', args=(g.id,)))
                # search for manager
                managers = Manager.objects.all()
                for m in managers:
                    if m.user == user:
                        auth_login(request, user)
                        return HttpResponseRedirect(reverse('Booking:manager', args=(m.id,)))
            else:
                return render(request, 'Booking/new/index.html', {
                    'error_message': "Account is not activated!"
                })
        else:
            return render(request, 'Booking/new/index.html', {
                'error_message': "Wrong Email address or Password!"
            })


# User logout
def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse('Booking:index'))


# User register form
def register(request):
    return render(request, 'Booking/new/register.html')


def registration(request):
    if request.method == 'POST':
        first_name = request.POST.get('fname')
        last_name = request.POST.get('lname')
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        # check password equality
        if password1 == password2:
            users = User.objects.all()
            for u in users:
                if u.username == username:
                    return render(request, 'Booking/new/register.html', context={
                        'error_message': "User already exists!"
                    })
            # user does not exist, create new
            new_user = User.objects.create_user(username, username, password1)
            new_user.is_staff = False
            new_user.is_active = False
            new_user.is_superuser = False
            new_user.save()
            # create activation link
            new_user_id = str(new_user.id)
            link = "http://127.0.0.1:8000/Booking/activation/" + new_user_id + "/"
            message_text = "Click on the following link to complete your registration\n\n" + link
            # sending email
            # send_mail('Restaurant - Profile Activation', message_text, 'carl.failure@gmail.com', [new_user.username],
            #          fail_silently=False)
            # creating guest object
            new_guest = Guest.objects.create(user=new_user)
            new_guest.user.first_name = first_name
            new_guest.user.last_name = last_name
            new_user.save()
            print("Successful! Guest inserted: " + str(new_guest))
            '''
            # back on page
            return render(request, 'Booking/register.html', context={
                'info_message': "Account created successfully. Email with activation link was sent!"
            })
            '''
            user = get_object_or_404(User, pk=new_user_id)
            if user is not None:
                user.is_active = True
                user.save()
                return render(request, 'Booking/new/index.html', context={
                    'info_message': "Account successfully activated!"
                })
        else:
            return render(request, 'Booking/new/register.html', context={
                'error_message': "Password wasn't repeated correctly!"
            })


# Manager's default page
@login_required(login_url='/')
def manager(request, manager_id):
    this_manager = get_object_or_404(Manager, pk=manager_id)
    yousers = Guest.objects.all

    return render(request, 'Booking/ManagerSide/manager.html', {
                                                    'manager': this_manager,
                                                    'users': yousers,
                                                    })


@login_required(login_url='/')
def dashboard(request, guest_id):
    this_guest = get_object_or_404(Guest, pk=guest_id)
    return render(request, 'Booking/new/dashboard.html', context={'guest': this_guest,
                                                                  })

# Manager's Look up reservations page
@login_required(login_url='/')
def managerOp(request, manager_id):
    this_manager = Manager.objects.get(pk=manager_id)
    opportunities_send = Opportunities.objects.all()

    return render(request, 'Booking/ManagerSide/Add_Projects.html', context={
        'manager': this_manager,
        'opportunities': opportunities_send,
    })


# dataCenter
@login_required(login_url='/')
def data_center(request, manager_id):
    this_manager = Manager.objects.get(pk=manager_id)

    return render(request, 'Booking/ManagerSide/datacenter.html', context={
        'manager': this_manager,
    })


@login_required(login_url='/')
def lookingup(request, manager_id):
    this_manager = get_object_or_404(Manager, pk=manager_id)
    print("we in the looking up function")
    this_branch = this_manager.restaurant
    if request.method == 'POST':
        reservations = []
        # get date and username from form
        user = request.POST.get('username')
        date_time = request.POST.get('datetime')
        branch_reservations = Reservation.objects.filter(restaurant=this_branch)
        # print(branch_reservations)
        isUser = False
        if user:
            isUser = True
            # print(str(user))
            for r in branch_reservations:
                # print(r.guest.user)
                if str(r.guest.user) == str(user):
                    reservations.append(r)
                    # print("added")
        if date_time:
            date_object = parser.parse(date_time)
            if isUser:
                print(date_object.day)
                print(date_object.month)
                temp = []
                for r in reservations:
                    if int(r.coming.day) == int(date_object.day) and int(r.coming.year) == int(
                            date_object.year) and int(r.coming.month) == int(date_object.month):
                        temp.append(r)
                reservations = temp

            else:
                # print(date_time)
                print(str(date_object))
                for r in branch_reservations:
                    print(str(r.coming))
                    if r.coming.day == date_object.day and r.coming.year == date_object.year and r.coming.month == date_object.month:
                        reservations.append(r)
                        print("added")
    if len(reservations) == 0:
        return render(request, 'Booking/lookup.html', context={
            'manager': this_manager,
            'error_message': "No Results found!"
        })
    else:
        return render(request, 'Booking/lookup.html', context={
            'manager': this_manager,
            'connections': reservations
        })


# Update Manager's profile
@login_required(login_url='/')
def updating(request, manager_id):
    this_manager = get_object_or_404(Manager, pk=manager_id)
    if request.method == 'POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if password1 == password2:
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            updated_manager = Manager.objects.get(pk=manager_id)
            # update profile
            updated_user = updated_manager.user
            updated_user.first_name = first_name
            updated_user.last_name = last_name
            updated_user.save()
            # update password if changed
            if password1 != '':
                updated_user.set_password(password1)
                updated_user.save()
            print("Success! Updated Manager: " + str(updated_manager))
            return HttpResponseRedirect(reverse('Booking:profiling', args=(manager_id,)))
        else:
            return render(request, 'Booking/manager_profile.html', context={
                'manager': this_manager,
                'error_message': "New password wasn't repeated correctly!"
            })

"""User pages"""


# Guest's default page
@login_required(login_url='/')
def guest(request, guest_id):
    form = Events.objects.all()
    this_guest = get_object_or_404(Guest, pk=guest_id)
    right_now = timezone.now()
    visits = Visit.objects.filter(guest=this_guest).filter(confirmed=True).filter(ending_time__lte=right_now)
    return render(request, 'Booking/guest.html', context={'form': form,
                                                          'guest': this_guest,
                                                          'visits': visits
                                                          })


# User friends
@login_required(login_url='/')
def friends(request, guest_id):
    # search for friendships where guest is user
    this_guest = get_object_or_404(Guest, pk=guest_id)
    # get number of friends
    friends_list = get_friends_list(this_guest)
    # calculate number of visits for every friend
    number_of_visits = []
    right_now = timezone.now()
    for ff in friends_list:
        number = len(Visit.objects.filter(guest=ff).filter(confirmed=True).filter(ending_time__lte=right_now))
        number_of_visits.append(number)
    friends_send = zip(friends_list, number_of_visits)
    return render(request, 'Booking/new/friends.html', context={
        'guest': this_guest,
        'friends': friends_send
    })


# Partners
@login_required(login_url='/')
def friends(request, guest_id):
    # search for friendships where guest is user
    this_guest = get_object_or_404(Guest, pk=guest_id)
    # get number of friends
    friends_list = get_friends_list(this_guest)
    # calculate number of visits for every friend
    number_of_visits = []
    right_now = timezone.now()
    for ff in friends_list:
        number = len(Visit.objects.filter(guest=ff).filter(confirmed=True).filter(ending_time__lte=right_now))
        number_of_visits.append(number)
    friends_send = zip(friends_list, number_of_visits)
    return render(request, 'Booking/new/friends.html', context={
        'guest': this_guest,
        'friends': friends_send
    })


# Search for friends
@login_required(login_url='/')
def search(request, guest_id):
    # find user
    this_guest = get_object_or_404(Guest, pk=guest_id)
    # select other users
    all_guests = Guest.objects.all().exclude(pk=guest_id)
    # find list of friends
    friends_list = get_friends_list(this_guest)
    # users for rendering
    if request.method == 'POST':
        query = request.POST.get('name').lower()
        render_users = []
        for g in all_guests:
            if g not in friends_list:
                # search for name and surname
                if (query in g.user.first_name.lower()) or (query in g.user.last_name.lower()):
                    render_users.append(g)
        # prepare data for resend
        number_of_visits = []
        right_now = timezone.now()
        for ff in friends_list:
            number = len(Visit.objects.filter(guest=ff).filter(confirmed=True).filter(ending_time__lte=right_now))
            number_of_visits.append(number)
        friends_send = zip(friends_list, number_of_visits)
        if len(render_users) == 0:
            return render(request, 'Booking/new/friends.html', context={
                'guest': this_guest,
                'friends': friends_send,
                'error_message': "No Users with given First Name and/or Last Name!"
            })
        else:
            return render(request, 'Booking/new/friends.html', context={
                'guest': this_guest,
                'friends': friends_send,
                'connections': render_users
            })


# Make new friendship
@login_required(login_url='/')
def connect(request, guest_id, connection_id):
    this_guest = get_object_or_404(Guest, pk=guest_id)
    new_friend = get_object_or_404(Guest, pk=connection_id)
    new_friendship = Friendship.objects.create(user=this_guest, friend=new_friend)
    new_friendship.save()
    print("Success! New Friendship: " + str(new_friendship))
    return HttpResponseRedirect(reverse('Booking:friends', args=(guest_id,)))


# Make new Application
@login_required(login_url='/')
def applying(request, guest_id, opportunity_id):
    this_guest = get_object_or_404(Guest, pk=guest_id)
    this_event = get_object_or_404(Opportunities, pk=opportunity_id)
    exists = Apply.objects.filter(user=this_guest, event=this_event).count()
    if exists == 0:
        new_apply = Apply.objects.create(user=this_guest, event=this_event)
        new_apply.save()
        print("Success! New Apply " + new_apply.__str__())
    return HttpResponseRedirect(reverse('Booking:projectlist', args=(guest_id,)))


# Make new Application
@login_required(login_url='/')
def clear_applying(request, guest_id, opportunity_id):
    this_guest = get_object_or_404(Guest, pk=guest_id)
    this_event = get_object_or_404(Opportunities, pk=opportunity_id)
    exists = Apply.objects.filter(user=this_guest, event=this_event).count()
    if exists > 0:
        Apply.objects.filter(user=this_guest, event=this_event).delete()
    return HttpResponseRedirect(reverse('Booking:projectlist', args=(guest_id,)))


# Remove friend
@login_required(login_url='/')
def disconnect(request, guest_id, friend_id):
    this_guest = get_object_or_404(Guest, pk=guest_id)
    this_friend = get_object_or_404(Guest, pk=friend_id)
    # first search friendships where guest is user
    user_friendship = Friendship.objects.filter(user=this_guest)
    for f in user_friendship:
        if f.friend == this_friend:
            f.delete()
            print("Success! Friendship deleted!")
            return HttpResponseRedirect(reverse('Booking:friends', args=(guest_id,)))
    # now search friendships where guest is friend
    friend_friendship = Friendship.objects.filter(friend=this_guest)
    for f in friend_friendship:
        if f.user == this_friend:
            f.delete()
            print("Success! Friendship deleted!")
            return HttpResponseRedirect(reverse('Booking:friends', args=(guest_id,)))


@login_required(login_url='/')
def profile(request, guest_id):
    # search for guest
    this_guest = get_object_or_404(Guest, pk=guest_id)
    # get friends
    friends_list = get_friends_list(this_guest)
    # show
    return render(request, 'Booking/new/profile.html', context={
        'guest': this_guest,
        'friends': friends_list
    })


# Update User profile info
@login_required(login_url='/')
def update(request, guest_id):
    this_guest = get_object_or_404(Guest, pk=guest_id)
    print("we here!")
    if request.method == 'POST':
        print("we in the if")
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if password1 == password2:
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            address = request.POST.get('address')
            updated_guest = Guest.objects.get(pk=guest_id)
            updated_guest.address = address
            updated_guest.save()
            print("Success! Updated Guest: " + str(updated_guest))
            # update profile
            updated_user = updated_guest.user
            updated_user.first_name = first_name
            updated_user.last_name = last_name
            updated_user.save()
            # update password if changed
            if password1 != '':
                updated_user.set_password(password1)
                updated_user.save()
                print("the pass has been changed")
            print("Success! Updated User: " + str(updated_user))
            print(reverse('Booking:profile', args=(guest_id,)))
            return HttpResponseRedirect(reverse('Booking:profile', args=(guest_id,)))
        else:
            friends_list = get_friends_list(this_guest)
            return render(request, 'Booking/new/profile.html', context={
                'guest': this_guest,
                'friends': friends_list,
                'error_message': "New password wasn't repeated correctly!"
            })


# Searching for friends on profile page
@login_required(login_url='/')
def searching(request, guest_id):
    # find user
    this_guest = get_object_or_404(Guest, pk=guest_id)
    # select other users
    all_guests = Guest.objects.all().exclude(pk=guest_id)
    # find list of friends
    friends_list = get_friends_list(this_guest)
    # users for rendering
    if request.method == 'POST':
        query = request.POST.get('name').lower()
        render_users = []
        for g in all_guests:
            if g not in friends_list:
                # search for name and surname
                if query in g.user.first_name.lower() or query in g.user.last_name.lower():
                    render_users.append(g)
        # prepare data for resend
        if len(render_users) == 0:
            return render(request, 'Booking/new/profile.html', context={
                'guest': this_guest,
                'friends': friends_list,
                'search_error': "No Users with given First Name and/or Last Name!"
            })
        else:
            return render(request, 'Booking/new/profile.html', context={
                'guest': this_guest,
                'friends': friends_list,
                'connections': render_users
            })


# get list of friends for given guest
def get_friends_list(this_guest):
    friendship_user = Friendship.objects.filter(user=this_guest)
    friendship_friend = Friendship.objects.filter(friend=this_guest)
    friends_list = []
    # selecting friends - friend
    for f in friendship_user:
        friend = f.friend
        if friend not in friends_list:
            friends_list.append(friend)
    # selecting friends - user
    for f in friendship_friend:
        friend = f.user
        if friend not in friends_list:
            friends_list.append(friend)
    return friends_list


# Display restaurant list with ratings
@login_required(login_url='/')
def projectList(request, guest_id):
    this_guest = get_object_or_404(Guest, pk=guest_id)
    opportunities_send = Opportunities.objects.all()
    for op in opportunities_send:
        print(op.id)
    applied = Apply.objects.filter(user=this_guest)
    apply_send = []
    for app in applied:
        apply_send.append(app.event.id)
    return render(request, 'Booking/new/projectList.html', context={
        'guest': this_guest,
        'opportunities': opportunities_send,
        'apply_send': apply_send
    })


# calculates restaurant's rating
def get_restaurant_rating(this_restaurant):
    list_of_visits = Visit.objects.filter(confirmed=True)
    s = 0
    c = 0
    for v in list_of_visits:
        if v.reservation.restaurant == this_restaurant:
            if v.grade is not None and v.grade >= 1:
                s += v.grade
                c += 1
    if c == 0:
        return 0
    else:
        r = s / c
        return round(r, 2)


# calculates restaurant's friends rating
def get_restaurants_friends_rating(this_restaurant, this_guest):
    guest_friends = get_friends_list(this_guest)
    all_visits = Visit.objects.filter(confirmed=True)
    list_of_visits = []
    for v in all_visits:
        if v.guest in guest_friends or v.guest == this_guest:
            list_of_visits.append(v)
    s = 0
    c = 0
    for v in list_of_visits:
        if v.reservation.restaurant == this_restaurant:
            if v.grade is not None and v.grade >= 1:
                s += v.grade
                c += 1
    if c == 0:
        return 0
    else:
        r = s / c
        return round(r, 2)


# shows restaurant's profile with menu
@login_required(login_url='/')
def restaurantmenu(request, guest_id, restaurant_id):
    this_guest = get_object_or_404(Guest, pk=guest_id)
    this_restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    menu_items = MenuItem.objects.filter(restaurant=this_restaurant)
    return render(request, 'Booking/restaurant_menu.html', context={
        'restaurant': this_restaurant,
        'guest': this_guest,
        'items': menu_items
    })


# shows history of guest's reservations
@login_required(login_url='/')
def myreservations(request, guest_id):
    this_guest = get_object_or_404(Guest, pk=guest_id)
    this_reservations = Reservation.objects.filter(guest=this_guest)
    return render(request, 'Booking/my_reservations.html', context={
        'guest': this_guest,
        'reservations': this_reservations
    })


# reservation time
@login_required(login_url='/')
def reservationtime(request, guest_id, restaurant_id):
    this_guest = get_object_or_404(Guest, pk=guest_id)
    this_restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    return render(request, 'Booking/reservation_time.html', context={
        'guest': this_guest,
        'restaurant': this_restaurant
    })


# setup reservation
@login_required(login_url='/')
def makereservation(request, guest_id, restaurant_id):
    # find guest and restaurant
    this_guest = get_object_or_404(Guest, pk=guest_id)
    this_restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    # find all reservations for given restaurant
    all_reservations = Reservation.objects.filter(restaurant=this_restaurant)
    # process form
    if request.method == 'POST':
        # get date from form
        date_time = request.POST.get('datetime')
        if date_time == '':
            return render(request, 'Booking/reservation_time.html', context={
                'guest': this_guest,
                'restaurant': this_restaurant,
                'error_message': "Please insert Date and Time"
            })
        coming = dt.strptime(date_time, '%d-%b-%Y %H:%M:%S')
        # localize to my timezone
        coming_time = pytz.utc.localize(coming)
        # time for comparison
        right_now = timezone.now()
        if coming_time < right_now:
            return render(request, 'Booking/reservation_time.html', context={
                'guest': this_guest,
                'restaurant': this_restaurant,
                'error_message': "It's impossible to reserve in the past!"
            })
        else:
            # get duration time
            duration = int(request.POST.get('duration'))
            # calculate ending time
            ending_time = coming_time + datetime.timedelta(hours=duration)
            # filter reservations with same time like new reservation
            taken_tables = 0
            for r in all_reservations:
                if are_overlap(coming_time, ending_time, r):
                    taken_tables += get_tables_from_reservation(r)
            if taken_tables == this_restaurant.tables:
                return render(request, 'Booking/reservation_time.html', context={
                    'guest': this_guest,
                    'restaurant': this_restaurant,
                    'error_message': "No available tables for given reservation period!"
                })
            else:
                # get all restaurant tables
                all_restaurant_tables = Table.objects.filter(restaurant=this_restaurant)
                # get reserved tables
                all_reserved_tables = []
                for r in all_reservations:
                    if are_overlap(coming_time, ending_time, r):
                        rt = reserved_tables_from_reservation(r)
                        if rt is not None:
                            for rrtt in rt:
                                all_reserved_tables.append(rrtt)
                # check if table is reserved or not
                for single_table in all_restaurant_tables:
                    if single_table in all_reserved_tables:
                        single_table.currently_free = False
                        single_table.save()
                    else:
                        single_table.currently_free = True
                        single_table.save()
                # tables are ready
                rows = range(1, this_restaurant.rows + 1)
                columns = range(1, this_restaurant.columns + 1)
                # create new reservation object
                new_reservation = Reservation.objects.create(coming=coming_time, duration=duration, guest=this_guest,
                                                             restaurant=this_restaurant)
                new_reservation.save()
                print("Success! Created Reservation: " + str(new_reservation))
                created_reservation = Reservation.objects.get(pk=new_reservation.id)
                render_tables = Table.objects.filter(restaurant=this_restaurant)
                return render(request, 'Booking/reservation_tables.html', context={
                    'guest': this_guest,
                    'restaurant': this_restaurant,
                    'reservation': created_reservation,
                    'tables': render_tables,
                    'rows': rows,
                    'columns': columns
                })


# check if two reservation periods overlap
def are_overlap(coming_time, ending_time, this_reservation):
    reservation_start = this_reservation.coming
    reservation_end = this_reservation.get_finishing_time()
    if coming_time <= reservation_start <= ending_time:
        return True
    else:
        if coming_time <= reservation_end <= ending_time:
            return True
        else:
            if reservation_start <= coming_time <= reservation_end:
                return True
            else:
                if reservation_start <= ending_time <= reservation_end:
                    return True
                else:
                    return False


# get number of tables from reservation
def get_tables_from_reservation(this_reservation):
    reserved_tables = ReservedTables.objects.filter(reservation=this_reservation)
    if reserved_tables is not None:
        return len(reserved_tables)
    else:
        return 0


# get table object from reservation
def reserved_tables_from_reservation(this_reservation):
    rt = ReservedTables.objects.filter(reservation=this_reservation)
    if rt is not None:
        ret_val = []
        for r in rt:
            ret_val.append(r.table)
        return ret_val
    else:
        return None


# reserving tables
@login_required(login_url='/')
@transaction.atomic
def reservetables(request, guest_id, restaurant_id, reservation_id):
    this_guest = get_object_or_404(Guest, pk=guest_id)
    this_restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    this_reservation = get_object_or_404(Reservation, pk=reservation_id)
    this_tables = Table.objects.filter(restaurant=this_restaurant)
    selected_tables = []
    if request.method == 'POST':
        for t in this_tables:
            if request.POST.get(str(t.id)):
                selected_tables.append(t)
        if len(selected_tables) == 0:
            delete_reservation = Reservation.objects.get(pk=reservation_id)
            delete_reservation.delete()
            print("Deleted Reservation!!!")
            return render(request, 'Booking/reservation_time.html', context={
                'guest': this_guest,
                'restaurant': this_restaurant,
                'error_message': "Unsuccessful Reservation! Tables weren't selected!"
            })
        # try to reserve tables
        try:
            with transaction.atomic():
                for t in selected_tables:
                    reserve_new_table = ReservedTables.objects.create(reservation=this_reservation, table=t)
                    reserve_new_table.save()
                    print("Success! Reserved table: " + str(t))
        # someonte reserve the table meanwhile
        except:
            delete_reservation = Reservation.objects.get(pk=reservation_id)
            delete_reservation.delete()
            print("Deleted Reservation!!!")
            return render(request, 'Booking/reservation_time.html', context={
                'guest': this_guest,
                'restaurant': this_restaurant,
                'error_message': "Unsuccessful Reservation! Selected tables are already reserved!"
            })

        # if everything was fine create new visit object
        stops = this_reservation.get_finishing_time()
        new_visit = Visit.objects.create(ending_time=stops, confirmed=True, reservation=this_reservation,
                                         guest=this_guest)
        new_visit.save()
        print("Success! Created new visit: " + str(new_visit))
        list_of_friends = get_friends_list(this_guest)
        return render(request, 'Booking/reservation_friends.html', context={
            'guest': this_guest,
            'restaurant': this_restaurant,
            'reservation': this_reservation,
            'friends': list_of_friends
        })


@login_required(login_url='')
def invitefriends(request, guest_id, restaurant_id, reservation_id):
    this_guest = get_object_or_404(Guest, pk=guest_id)
    this_restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    this_reservation = get_object_or_404(Reservation, pk=reservation_id)
    # get friends list
    friend_list = get_friends_list(this_guest)
    selected_friends = []
    if request.method == 'POST':
        # collect friends
        for f in friend_list:
            if request.POST.get(str(f.id)):
                selected_friends.append(f)
        # if there is no selected friends, send to my reservations
        if len(selected_friends) == 0:
            return HttpResponseRedirect(reverse('Booking:myreservations', args=(guest_id,)))
        else:
            # send mail invitations and create visit objects
            stops = this_reservation.get_finishing_time()
            for this_friend in selected_friends:
                print("Working for: " + str(this_friend))
                friend_guest = get_object_or_404(Guest, pk=this_friend.id)
                new_visit = Visit.objects.create(ending_time=stops, confirmed=False, reservation=this_reservation,
                                                 guest=friend_guest)
                new_visit.save()
                print("Success! Created new visit: " + str(new_visit))
                # send_mail
                message_text = "You got an invitation to visit Restaurant. Login and follow link to see more:\n\n"
                link_text = "http://127.0.0.1:8000/Booking/showinvitation/" + str(
                    friend_guest.id) + "/" + reservation_id + "/" + str(new_visit.id) + "/"
                # text_to_send = message_text + link_text
                # send_mail('Restaurant - Invitation', text_to_send, 'test@gmail.com', [friend_guest.user.username],
                #          fail_silently=False)
                # print("Success! Mail sent to: " + str(friend_guest))
            # all finished
            return HttpResponseRedirect(reverse('Booking:myreservations', args=(guest_id,)))


@login_required(login_url='/')
def showinvitation(request, guest_id, reservation_id, visit_id):
    this_guest = get_object_or_404(Guest, pk=guest_id)
    this_reservation = get_object_or_404(Reservation, pk=reservation_id)
    this_visit = get_object_or_404(Visit, pk=visit_id)
    right_now = timezone.now()
    if right_now > this_visit.ending_time:
        return render(request, 'Booking/reservation_confirm.html', context={
            'guest': this_guest,
            'reservation': this_reservation,
            'visit': this_visit,
            'show': False,
            'error_message': "Time's up!"
        })
    else:
        if this_visit.confirmed:
            return render(request, 'Booking/reservation_confirm.html', context={
                'guest': this_guest,
                'reservation': this_reservation,
                'visit': this_visit,
                'show': False,
                'info_message': "Invitation already confirmed!"
            })
        else:
            return render(request, 'Booking/reservation_confirm.html', context={
                'guest': this_guest,
                'reservation': this_reservation,
                'visit': this_visit,
                'show': True
            })


@login_required(login_url='/')
def acceptinvitation(request, guest_id, reservation_id, visit_id):
    this_guest = get_object_or_404(Guest, pk=guest_id)
    this_reservation = get_object_or_404(Reservation, pk=reservation_id)
    this_visit = get_object_or_404(Visit, pk=visit_id)
    new_visit = Visit.objects.get(pk=visit_id)
    new_visit.confirmed = True
    new_visit.save()
    print("Success! Confirmed Visit: " + str(this_visit))
    return render(request, 'Booking/reservation_confirm.html', context={
        'guest': this_guest,
        'reservation': this_reservation,
        'visit': this_visit,
        'info_message': "Invitation Accepted!"
    })


@login_required(login_url='/')
def addGadget(request, manager_id):
    this_manager = get_object_or_404(Manager, pk=manager_id)
    gadgets = Gadget.objects.all()

    if request.POST:
        postedPrice = request.POST['price']
        postedName = request.POST['name']
        postedNumber = request.POST['Number']
        num = Gadget.objects.filter(name=postedName).count()

        print('num is = ' + str(num))
        if num < 1 and postedPrice and postedName:
            g = Gadget()
            g.price = postedPrice
            g.name = postedName
            g.Number = postedNumber
            g.save()
            return HttpResponseRedirect(reverse('Booking:addGadget', args=(manager_id,)))
        else:
            return render(request, 'Booking/add_gadgets.html', context={
                'manager': this_manager,
                'gadgets': gadgets,
                'error_message': "please fill all the information correctly and make sure the gadget name doesn't "
                                 "already exists! "
            })
    else:
        return render(request, 'Booking/add_gadgets.html', context={'manager': this_manager, 'gadgets': gadgets})




@login_required(login_url='/')
def addOpportunity(request, manager_id):
    this_manager = get_object_or_404(Manager, pk=manager_id)
    opportunity = Opportunities.objects.all()

    if request.POST:
        postedName = request.POST['name']
        postedDescription = request.POST['description']
        postedLocation = request.POST['location']
        postedEmployer = request.POST['employer']
        postedCategory = request.POST['category']

        # num = Opportunities.objects.filter(name=postedName).count()

        o = Opportunities()
        o.name = postedName
        o.description = postedDescription
        o.location = postedLocation
        o.employer = postedEmployer
        if 'isRemote' in request.POST:
            o.is_remote = True
        else:
            o.is_remote = False
        o.category = postedCategory
        o.save()
        return render(request, 'Booking/ManagerSide/Add_Projects.html', context={'manager': this_manager, 'opportunities': opportunity})



@login_required(login_url='/')
def reserveGame(request, guest_id):
    this_guest = get_object_or_404(Guest, pk=guest_id)

    games = Game.objects.all()
    if request.POST:
        g = Game()
        g.name = request.POST['game_choice']
        g.people = request.POST['numOfPeople']
        g.date_reserved = request.POST['date']
        g.reserver_id = guest_id
        g.save()

    return render(request,
                  "Booking/reserve_game.html",
                  context=
                  {'games': games,
                   'guest': this_guest, }
                  )


@login_required(login_url='/')
def viewGadgets(request, guest_id):
    this_guest = get_object_or_404(Guest, pk=guest_id)
    gadgets = Gadget.objects.all()
    return render(request,
                  "Booking/view_gadgets.html",
                  context=
                  {'gadgets': gadgets,
                   'guest': this_guest, }
                  )


@login_required(login_url='/')
def viewTransactions(request, manager_id):
    this_manager = get_object_or_404(Manager, pk=manager_id)
    transactions = Transaction.objects.all()
    gadgets = Gadget.objects.all()

    return render(request,
                  "Booking/manage_cash.html",
                  context=
                  {'transactions': transactions,
                   'manager': this_manager,
                   'gadgets': gadgets}
                  )


@login_required(login_url='/')
def addTransaction(request, manager_id):
    this_manager = get_object_or_404(Manager, pk=manager_id)
    gadgets = Gadget.objects.all()

    if request.POST:
        transactions = Transaction.objects.all()
        t = Transaction()
        t.amount = request.POST['amount']
        t.transaction_type = request.POST['type']
        t.item = request.POST['item']
        g = Gadget.objects.filter(name=t.item).get(name=t.item)
        n = g.Number
        if t.transaction_type == 'sell':
            Gadget.objects.filter(name=t.item).update(Number=n - int(t.amount))
            t.save()
        elif t.transaction_type == 'buy':
            Gadget.objects.filter(name=t.item).update(Number=n + int(t.amount))
            t.save()
    return render(request, 'Booking/manage_cash.html',
                  context={'manager': this_manager, 'gadgets': gadgets, 'transactions': transactions})
