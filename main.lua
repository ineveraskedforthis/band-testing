function sum_rgb(image, x, y)
	r, g, b, a = ImageData
end

-- Save copied tables in `copies`, indexed by original table.
function deepcopy(orig, copies)
    copies = copies or {}
    local orig_type = type(orig)
    local copy
    if orig_type == 'table' then
        if copies[orig] then
            copy = copies[orig]
        else
            copy = {}
            copies[orig] = copy
            for orig_key, orig_value in next, orig, nil do
                copy[deepcopy(orig_key, copies)] = deepcopy(orig_value, copies)
            end
            setmetatable(copy, deepcopy(getmetatable(orig), copies))
        end
    else -- number, string, boolean, etc
        copy = orig
    end
    return copy
end
function set_global_variables()
	SCREEN_W = 1000
	SCREEN_H = 800
    love.window.setMode(SCREEN_W, SCREEN_H)
    
	directions = {{-1, 0}, {1, 0}, {0, -1}, {0, 1}, {-1, -1}, {1, 1}, {1, -1}, {-1, 1}}
    morae = {}
    a = {'s', 'k', 't', 'm', 'n', 'h', 'r', ''}
    b = {'i', 'e', 'u', 'a', 'o'}
    morae_amount = 0
    for i = 1, 8 do
        for j = 1, 5 do
            morae_amount = morae_amount + 1
            morae[morae_amount] = a[i] .. b[j]
        end 
    end
    
    tribes_map = love.image.newImageData(600, 800)
    
    FOOD_MAP = {}
    for i = 0, 600 do
        FOOD_MAP[i] = {}
        for j = 0, 600 do
            FOOD_MAP[i][j] = 1000
        end
    end
    
    LOOKING_FOR_FRIENDS = {}
    for i = 0, 600 do
        LOOKING_FOR_FRIENDS[i] = {}
        for j = 0, 600 do
            LOOKING_FOR_FRIENDS[i][j] = {}
        end
    end
    
    LOOKING_FOR_FRIENDS_amount = {}
    for i = 0, 600 do
        LOOKING_FOR_FRIENDS_amount[i] = {}
        for j = 0, 600 do
            LOOKING_FOR_FRIENDS_amount[i][j] = 0
        end
    end
    
    INSIDE_AGE_TO_BORN = 4 * 30 * 5
    -- INSIDE_AGE_TO_BORN = 4
    MATING_AGE = 4 * 30 * 12 * 3 
    -- MATING_AGE = 200
    PREGNANCY_CHANCE = 0.0009
    DEATH_AGE = 4 * 30 * 12 * 10 
    DEATH_CHANCE = 0.001
    
    amount_of_characters = 0
    character_location = {}
    character_name = {}
    character_age = {}
    character_parent = {}
    character_stash = {}
    -- food 
    -- water
    
    character_inside_character_age = {}
    -- pregnancy time
    
    character_sex = {}
    character_dead = {}
    -- 0 - female
    -- 1 - male
    
    -- stats
    character_charisma = {}
    character_loyalty = {}
    character_starvation = {}
    
    character_friends = {}
    character_friends_type = {}
    character_amount_of_friends = {}
    -- friends
    
    character_leader = {}
    -- character will follow leader in his journey
    
    character_ai_type = {} 
    -- 0 - content
    -- 1 - ambitious
    
    character_action = {}
    -- 0 - migrate
    -- 1 - gather
    -- 2 - sleep
    -- 3 - idle
    
    LEFT_new_character = 0
    RIGHT_new_character = 0
    new_characters_queue = {}
    
    create_character(MATING_AGE, 0, 0, {300, 300} )
    create_character(MATING_AGE, 0, 1, {300, 300} )
    add_friend(1, 2, "friend")    
    add_friend(2, 1, "friend")
    set_leader(2, 1)
    set_leader(1, 1)
    
    create_character(MATING_AGE, 0, 0, {100, 100} )
    create_character(MATING_AGE, 0, 1, {100, 100} )
    add_friend(3, 4, "friend")    
    add_friend(4, 3, "friend")
    set_leader(4, 3)
    set_leader(3, 3)
    
    player = 1
    
    day_part = 0
    day_part_selected = 1
    
    major_update_tick = 0
end


-- getters
function get_age(i) 
    if i <= 0 then
        return 9999
    end
    return math.floor(character_age[i] / 4 / 30 / 12)
end
function get_local_food(i)
    local x = character_location[i][1]
    local y = character_location[i][2]
    return FOOD_MAP[x][y]
end
function get_character_name(i)
    if (i > 0) then
        return character_name[i]
    end
    return "Creator of the world."
end

-- setters
function set_leader(i, j)
    print(tostring(i) .. " " .. tostring(j))
    character_leader[i] = j
end



-- updaters
function update_characters()
    -- update character age
    for i = 1, amount_of_characters do        
        character_age[i] = character_age[i] + 1
    end
    
    -- die
    for i = 1, amount_of_characters do
        if not character_dead[i] then
            if character_age[i] > DEATH_AGE then
                local dice = math.random()
                if dice < DEATH_CHANCE then
                    kill(i, "old")
                end
            end
            if character_starvation[i] > 10 then
                kill(i, "starvation")
            end
        end
    end
    
    -- update pregnancy
    for i = 1, amount_of_characters do
        character_update_pregnancy(i)
    end    
    
    --pregnancy dice roll
    for i = 1, amount_of_characters do
        character_pregnancy_roll(i)
    end
    
    -- ai update
    for i = 1, amount_of_characters do
        character_ai_update_actions(i)
    end    
    
    
    -- action 
    for i = 1, amount_of_characters do
        if not character_dead[i] then
            if character_action[i][day_part] == 0 then
                character_migrate(i)
            elseif character_action[i][day_part] == 1 then
                character_collect_food(i)
            elseif character_action[i][day_part] == 2 then
                character_look_for_friends(i)
            end
        end
    end
    
    -- share stuff
    for i = 1, amount_of_characters do
        character_share_stuff(i)
    end
    
    
    -- consume
    for i = 1, amount_of_characters do
        if not character_dead[i] then
        
            local food = character_stash[i].food
            if food >= 1 then
                character_stash[i].food = food - 1
                if character_starvation[i] > 0 then
                    character_starvation[i] = character_starvation[i] - 1
                end
            else
                character_starvation[i] = character_starvation[i] + 1
            end
          
        end
    end
 
    -- born characters
    for i = LEFT_new_character, RIGHT_new_character - 1 do
        local sex = math.random(2) - 1
        local parent = new_characters_queue[i]
        create_character(0, parent, sex, character_location[parent])
        
        new_characters_queue[i] = nil
    end
    LEFT_new_character = RIGHT_new_character
    
    
    -- update_leaders
    if (day_part == 1) then    
        for i = 1, amount_of_characters do
            character_update_leader(i)
        end
    end
    
    -- follow_leaders
    for i = 1, amount_of_characters do
        if not character_dead[i] then
            local leader = character_leader[i]
            if (leader > 0) then 
                local x = character_location[leader][1]
                local y = character_location[leader][2]

                character_location[i][1] = x
                character_location[i][2] = y
            end
        end
    end
end

function update_map() 
    for i = 1, 400 do
        for j = 1, 400 do
            for k = 1, LOOKING_FOR_FRIENDS_amount[i][j] do
                local dice = math.random()
                if dice > 0.5 then
                    local ind = math.random(LOOKING_FOR_FRIENDS_amount[i][j])
                    local p_friend = LOOKING_FOR_FRIENDS[i][j][ind]
                    local character = LOOKING_FOR_FRIENDS[i][j][k]
                    if (ind ~= k) then
                        add_friend(character, p_friend, "friend")
                        add_friend(p_friend, character, "friend")
                    end
                end
            end
        end
    end
end

-- generators
function gen_name()
    local n = math.random(3) + 1
    local res = ''
    for i = 1, 2 do
        local j = math.random(morae_amount)
        res = res .. morae[j]
    end
    return res
end



---- actions
function kill(i, reason)
    print("kill " .. tostring(i) .. " " .. reason)
    character_dead[i] = true
end


-- create 
function create_character(age, parent, sex, location, ai_type)
    amount_of_characters = amount_of_characters + 1
    
    character_dead[amount_of_characters] = false
    
    character_location[amount_of_characters] = {}
    character_location[amount_of_characters][1] = location[1]
    character_location[amount_of_characters][2] = location[2]
    character_name[amount_of_characters] = gen_name()
    character_age[amount_of_characters] = age
    character_starvation[amount_of_characters] = 0
    
    character_stash[amount_of_characters] = {food=0, water=0}
    
    character_inside_character_age[amount_of_characters] = -1
    character_sex[amount_of_characters] = sex
    character_charisma[amount_of_characters] = math.random(10) + math.random(5) + math.random(5)
    character_loyalty[amount_of_characters] = 50
    
    character_parent[amount_of_characters] = parent
    set_leader(amount_of_characters, parent)
    character_leader[amount_of_characters] = parent
    
    character_amount_of_friends[amount_of_characters] = 0
    character_friends[amount_of_characters] = {}
    character_friends_type[amount_of_characters] = {}
    
    if ai_type == nil then
        local dice = math.random()
        if (dice > 0.1) then 
            ai_type = "content"
        else
            ai_type = "ambitious"
        end
    end
    
    character_ai_type[amount_of_characters] = ai_type
    character_action[amount_of_characters] = {2, 2, 2, 2}
    
    add_friend(amount_of_characters, parent, "parent")
    if parent > 0 then 
        add_friend(parent, amount_of_characters, "child")
    end
end

-- characters
function character_migrate(i) 
    if character_dead[i] then
        return
    end
    local j = math.random(8)
    local x = character_location[i][1] + directions[j][1]
    local y = character_location[i][2] + directions[j][2]
    if valid_position(x, y) then
        character_location[i][1] = x
        character_location[i][2] = y
    end
end


function character_ai_update_actions(i)
    if character_dead[i] then
        return
    end
    if character_age[i] < MATING_AGE * 0.5 then
        -- if child is young, he is idling, and looking for friends
        character_action[i][1] = 3
        character_action[i][2] = 3
        character_action[i][3] = 2
        character_action[i][4] = 2
    elseif character_age[i] < MATING_AGE then 
        -- after growing up a bit he starts gathering food on his own
        character_action[i][1] = 1
        character_action[i][2] = 2
        character_action[i][3] = 2
        character_action[i][4] = 2
    elseif character_leader[i] == i then
        -- leaders spend some time trying to move with their tribes while still collecting food
        character_action[i][1] = 1
        character_action[i][2] = 0
        character_action[i][3] = 2
        character_action[i][4] = 2
    else
        character_action[i][1] = 1
        character_action[i][2] = 1
        character_action[i][3] = 2
        character_action[i][4] = 2
    end
end


function character_pregnancy_roll(i)
    if character_dead[i] then
        return
    end
    if character_inside_character_age[i] > -1 or character_sex[i] == 1 or character_age[i] < MATING_AGE then
        return
    end
    for j = 1, character_amount_of_friends[i] do
        local friend = character_friends[i][j]
        local friend_type = character_friends_type[i][j]
        if friend_type == 'friend' then
            local dice = math.random()
            if dice < PREGNANCY_CHANCE  then
                character_inside_character_age[i] = 0
            end
        end
    end
end


function character_collect_food(i)
    if character_dead[i] then
        return
    end
    local dice = math.random()
    local local_food = FOOD_MAP[character_location[i][1]][character_location[i][2]]
    if (dice < 0.99 * local_food / 1000) and local_food > 10 then
        character_stash[i].food = character_stash[i].food + 10
        FOOD_MAP[character_location[i][1]][character_location[i][2]] = FOOD_MAP[character_location[i][1]][character_location[i][2]] - 10
    end
end

function character_share_stuff(i)
    if character_dead[i] then
        return
    end
    for j = 1, character_amount_of_friends[i] do
        local count = 0
        local friend = character_friends[i][j]
        local friend_type = character_friends_type[i][j]
        if not character_dead[friend]  and character_stash[i].food > 20 + count * 4 and friend_type == 'child' and character_starvation[friend] > 0 then
            character_transfer(i, friend, 'food', 1)
            count = count + 1
        end
    end
end

function character_transfer(i, j, tag, x)
    if character_stash[i][tag] > x then
        character_stash[i][tag] = character_stash[i][tag] - x
        character_stash[j][tag] = character_stash[j][tag] + x
    end
end

function character_look_for_friends(i)
    if character_dead[i] then
        return
    end
    local x = character_location[i][1]
    local y = character_location[i][2]
    local n = LOOKING_FOR_FRIENDS_amount[x][y] + 1
    LOOKING_FOR_FRIENDS_amount[x][y] = n
    LOOKING_FOR_FRIENDS[x][y][n] = i
end


function character_update_pregnancy(i) 
    if character_dead[i] then
        return
    end
    if character_inside_character_age[i] == -1 then
        return
    end
    
    character_inside_character_age[i] = character_inside_character_age[i] + 1
    if character_inside_character_age[i] > INSIDE_AGE_TO_BORN then
        new_child(i)
        character_inside_character_age[i] = -1
    end
end


function character_update_leader(character)
    if character_dead[i] then
        return
    end
    if character_leader[character] == character then
        return
    end
    if character_dead[character_leader[character]] then
        set_leader(character, character)
    end
    if character_ai_type[character] == "ambitious" then
        return
    end
    if character_loyalty[character] > 80 then
        return
    end
    if character_age[character] < MATING_AGE then
        return
    end
    local n = character_amount_of_friends[character]
    for i = 1, n do
        local friend = character_friends[character][i]
        if (get_age(friend) > MATING_AGE) and (get_age(friend) < 100) and (character_friends_type[character][i] == "friend") and (character_ai_type[friend] == "ambitious") and (character_ai_type[character] == "content") then
            local dice = math.random(20)
            if character_charisma[friend] >= dice then
                set_leader(character, friend)
                character_loyalty[character] = 100
            end
        end
    end
end


function add_friend(character, friend, friend_type)
    if character == friend then
        return
    end
    local n = character_amount_of_friends[character] + 1
    for i = 1, n do
        if character_friends[character][i] == friend then
            return
        end
    end
    character_amount_of_friends[character] = n
    character_friends[character][n] = friend
    character_friends_type[character][n] = friend_type
end


-- child queue
function new_child(parent)
    new_characters_queue[RIGHT_new_character] = parent
    RIGHT_new_character = RIGHT_new_character + 1
end



-- validators
function valid_position(x, y)
    if (x > 0 and x <= 400) and (y > 0 and y <= 400) then
        return true
    end
    return false
end






-- main functions

function love.load()
	set_global_variables()
    math.randomseed(0)
	-- mapImageData = love.image.newImageData("map2.png")
	-- riversImageData = love.image.newImageData("rivers.png")
	-- fertilityImageData = love.image.newImageData("fertility.png")
	-- forestImageData = love.image.newImageData("forest.png")
end

function build_image()
    tribes_map = love.image.newImageData(500, 500)
    -- print('______________')
    for i = 1, amount_of_characters do
        if not character_dead[i] and character_leader[i] == i then
            -- print(i, character_location[i][1], character_location[i][2])
            tribes_map:setPixel(character_location[i][1], character_location[i][2], 1, 0, 0, 1)
        end
    end
    return love.graphics.newImage(tribes_map)
end

function love.draw()
    image = build_image()
    love.graphics.draw(image, 1, 1)
    love.graphics.rectangle("line", 0, 0, 401, 401)
    
    
    love.graphics.print("Your age: " .. tostring(get_age(player)) .. " years", 405, 00)
    love.graphics.print("Your name: " .. get_character_name(player), 405, 20)
    if character_inside_character_age[player] > -1 then
        love.graphics.print("Pregnant", 405, 040)
    end
    love.graphics.rectangle("line", 401, 0, 598, 201)
    
    
    
    love.graphics.print("Current action: ", 530, 100)
    
    love.graphics.print("morning", 405, 205)
    love.graphics.print("day", 405, 225)
    love.graphics.print("evening", 405, 245)
    love.graphics.print("night", 405, 265)
    
    for i = 1, 4 do
        local h = 205 + (i - 1) * 20
        if i == day_part_selected then
            love.graphics.rectangle("line", 401, h, 598, 19)
        end    
        if (character_action[player][i] == 0) then
            love.graphics.print("[q]Migrate!",                    465, h)
            love.graphics.print({{1, 0, 0, 0.5}, "[w]Gather"},    565, h)
            love.graphics.print({{1, 0, 0, 0.5}, "[e]Sleep"},     665, h)
        elseif character_action[player][i] == 1 then
            love.graphics.print({{1, 0, 0, 0.5}, "[q]Migrate"},   465, h)
            love.graphics.print("[w]Gather!",                     565, h)
            love.graphics.print({{1, 0, 0, 0.5}, "[e]Sleep"},     665, h)
        elseif character_action[player][i] == 2 then
            love.graphics.print({{1, 0, 0, 0.5}, "[q]Migrate"},   465, h)
            love.graphics.print({{1, 0, 0, 0.5}, "[w]Gather"},    565, h)
            love.graphics.print("[e]Sleep!",                      665, h)
        end
    end
    love.graphics.rectangle("line", 401, 201, 598, 201)
    
    
    
    local stash = character_stash[player]
    love.graphics.print("food: " .. tostring(stash.food), 530, 20)
    love.graphics.print("water: " .. tostring(stash.water), 530, 40)
    
    
    local leaders = {}
    local leader_amount = 0
    for i = 1, amount_of_characters do
        if not character_dead[i] and character_leader[i] == i then
            leader_amount = leader_amount + 1
            leaders[leader_amount] = i
            if character_ai_type[i] == "ambitious" then
                love.graphics.setColor(1, 0, 0)
            else 
                love.graphics.setColor(1, 1, 1)
            end
            love.graphics.circle("fill", 20 + leader_amount * 50, 420, 3)
        end
    end
    
    local subleaders = {}
    local subleader_amount = 0
    for j = 1, leader_amount do
        for i = 1, amount_of_characters do
            if not character_dead[i] and character_leader[i] == leaders[j] and character_leader[i] ~= i then
                subleader_amount = subleader_amount + 1
                subleaders[subleader_amount] = i
                if character_ai_type[i] == "ambitious" then
                    love.graphics.setColor(1, 0, 0)
                else 
                    love.graphics.setColor(1, 1, 1)
                end
                love.graphics.circle("fill", 20 + subleader_amount * 30, 450, 3)
                love.graphics.line(20 + subleader_amount * 30, 450, 20 + j * 50, 420)
            end
        end
    end
    
    -- local subsubleaders = {}
    -- local subsubleader_amount = 0
    -- for j = 1, subleader_amount do
        -- for i = 1, amount_of_characters do
            -- if not character_dead[i] and character_leader[i] == subleaders[j] and character_leader[i] ~= i then
                -- subsubleader_amount = subsubleader_amount + 1
                -- subsubleaders[subsubleader_amount] = i
                -- if character_ai_type[i] == "ambitious" then
                    -- love.graphics.setColor(1, 0, 0)
                -- else 
                    -- love.graphics.setColor(1, 1, 1)
                -- end
                -- love.graphics.circle("fill", 20 + subsubleader_amount * 15, 490, 3)
                -- love.graphics.line(20 + subsubleader_amount * 15, 490, 20 + j * 30, 450)
            -- end
        -- end
    -- end
    
    -- local subsubsubleaders = {}
    -- local subsubsubleader_amount = 0
    -- for j = 1, subsubleader_amount do
        -- for i = 1, amount_of_characters do
            -- if not character_dead[i] and character_leader[i] == subsubleaders[j] and character_leader[i] ~= i then
                -- subsubsubleader_amount = subsubsubleader_amount + 1
                -- subsubsubleaders[subsubsubleader_amount] = i
                -- if character_ai_type[i] == "ambitious" then
                    -- love.graphics.setColor(1, 0, 0)
                -- else 
                    -- love.graphics.setColor(1, 1, 1)
                -- end
                -- love.graphics.circle("fill", 20 + subsubsubleader_amount * 5, 540, 3)
                -- love.graphics.line(20 + subsubsubleader_amount * 5, 540, 20 + j * 15, 490)
            -- end
        -- end
    -- end
    
    -- local subsubsubsubleaders = {}
    -- local subsubsubsubleader_amount = 0
    -- for j = 1, subsubsubleader_amount do
        -- for i = 1, amount_of_characters do
            -- if not character_dead[i] and character_leader[i] == subsubsubleaders[j] and character_leader[i] ~= i then
                -- subsubsubsubleader_amount = subsubsubsubleader_amount + 1
                -- subsubsubsubleaders[subsubsubleader_amount] = i
                -- if character_ai_type[i] == "ambitious" then
                    -- love.graphics.setColor(1, 0, 0)
                -- else 
                    -- love.graphics.setColor(1, 1, 1)
                -- end
                -- love.graphics.circle("fill", 20 + subsubsubsubleader_amount * 5, 560, 3)
                -- love.graphics.line(20 + subsubsubsubleader_amount * 5, 560, 20 + j * 5, 540)
            -- end
        -- end
    -- end
    
    love.graphics.setColor(1, 1, 1)
    
    -- love.graphics.print("Friends: ", 650, 00)
    -- local n = character_amount_of_friends[player]    
    -- for i = 1, n do
        -- local friend = character_friends[player][i]
        -- local friend_type = character_friends_type[player][i]
        -- love.graphics.print(get_character_name(friend), 650, 00 + i * 20)
        -- love.graphics.print(friend_type, 900, 00 + i * 20)
        -- love.graphics.print(tostring(get_age(friend)) .. " years old", 800, 00 + i * 20)
        -- love.graphics.print(tostring(character_sex[friend]), 950, 00 + i * 20)
    -- end 
    
    
    
end

function love.update()
    
    -- if love.keyboard.isDown('a') then
        update_characters()
        update_map()
    -- end
    
    if love.keyboard.isDown('q') then
        character_action[player][day_part_selected] = 0
    end
    if love.keyboard.isDown('w') then
        character_action[player][day_part_selected] = 1
    end
    if love.keyboard.isDown('e') then
        character_action[player][day_part_selected] = 2
    end
    
    if love.keyboard.isDown('1') then
        day_part_selected = 1
    end
    if love.keyboard.isDown('2') then
        day_part_selected = 2
    end
    if love.keyboard.isDown('3') then
        day_part_selected = 3
    end
    if love.keyboard.isDown('4') then
        day_part_selected = 4
    end
    
    day_part = (day_part + 1) % 4
end